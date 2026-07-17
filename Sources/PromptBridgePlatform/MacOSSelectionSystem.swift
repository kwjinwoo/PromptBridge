import AppKit
@preconcurrency import ApplicationServices
import Foundation
import PromptBridgeCore

/// `NSPasteboard`, Accessibility, and synthetic-key adapter for the Phase 3 prototype.
public final class MacOSSelectionSystem: SelectionSystem, @unchecked Sendable {
    private let pasteboard: NSPasteboard
    private let pasteSettleTime: TimeInterval

    /// Creates an adapter around the general system pasteboard.
    public init(
        pasteboard: NSPasteboard = .general,
        pasteSettleTime: TimeInterval = 0.05
    ) {
        self.pasteboard = pasteboard
        self.pasteSettleTime = pasteSettleTime
    }

    /// Whether Accessibility currently authorizes focus inspection and key events.
    public var hasAccessibilityPermission: Bool {
        AXIsProcessTrusted()
    }

    /// Requests the system Accessibility consent prompt for this executable.
    @discardableResult
    public func requestAccessibilityPermission() -> Bool {
        let promptKey = kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String
        let options = [promptKey: true] as CFDictionary
        return AXIsProcessTrustedWithOptions(options)
    }

    /// Current system pasteboard generation.
    public var clipboardChangeCount: Int {
        pasteboard.changeCount
    }

    /// Captures all available pasteboard items and representations in memory.
    public func captureClipboard() -> ClipboardSnapshot {
        let items = (pasteboard.pasteboardItems ?? []).map { item in
            let representations = Dictionary(
                uniqueKeysWithValues: item.types.compactMap { type in
                    item.data(forType: type).map { (type.rawValue, $0) }
                }
            )
            return PasteboardItem(representations: representations)
        }
        return ClipboardSnapshot(items: items)
    }

    /// Copies selected text while retaining the application and focused-element identity.
    public func captureSelection(copyTimeout: TimeInterval) throws -> CapturedSelection {
        let original = captureClipboard()
        let context = try currentTargetContext()
        let baseline = pasteboard.changeCount
        try postShortcut(keyCode: 8)
        let deadline = Date().addingTimeInterval(copyTimeout)
        while pasteboard.changeCount == baseline, Date() < deadline {
            Thread.sleep(forTimeInterval: 0.01)
        }
        guard pasteboard.changeCount != baseline else {
            throw CaptureError.copyTimedOut
        }
        let copiedChangeCount = pasteboard.changeCount
        guard let source = pasteboard.string(forType: .string), !source.isEmpty else {
            restoreClipboard(original, ifChangeCount: copiedChangeCount)
            throw CaptureError.noTextSelection
        }
        return CapturedSelection(
            source: source,
            context: context,
            clipboardChangeCount: copiedChangeCount
        )
    }

    /// Returns the frontmost process and focused Accessibility element identity.
    public func currentTargetContext() throws -> TargetContext {
        guard let application = NSWorkspace.shared.frontmostApplication else {
            throw CaptureError.contextUnavailable
        }
        let accessibilityApplication = AXUIElementCreateApplication(application.processIdentifier)
        var focusedValue: CFTypeRef?
        let result = AXUIElementCopyAttributeValue(
            accessibilityApplication,
            kAXFocusedUIElementAttribute as CFString,
            &focusedValue
        )
        guard result == .success, let focusedValue else {
            throw CaptureError.contextUnavailable
        }
        return TargetContext(
            applicationPID: application.processIdentifier,
            focusedElementID: Int(bitPattern: CFHash(focusedValue))
        )
    }

    /// Places validated text on the pasteboard and reports its owned generation.
    public func writeForPaste(_ text: String) -> ClipboardWriteResult {
        pasteboard.clearContents()
        let succeeded = pasteboard.setString(text, forType: .string)
        return ClipboardWriteResult(
            succeeded: succeeded,
            changeCount: pasteboard.changeCount
        )
    }

    /// Sends Command-V to the unchanged focused target.
    public func paste() throws {
        try postShortcut(keyCode: 9)
        // CGEvent posting is asynchronous; retain transformed clipboard ownership until
        // the target event loop has had a bounded opportunity to consume the paste.
        Thread.sleep(forTimeInterval: pasteSettleTime)
    }

    /// Restores every captured representation only while PromptBridge owns the pasteboard.
    @discardableResult
    public func restoreClipboard(
        _ snapshot: ClipboardSnapshot,
        ifChangeCount expected: Int
    ) -> Bool {
        guard pasteboard.changeCount == expected else {
            return false
        }
        pasteboard.clearContents()
        guard !snapshot.items.isEmpty else {
            return true
        }
        let nativeItems = snapshot.items.map { item in
            let nativeItem = NSPasteboardItem()
            for (type, data) in item.representations {
                nativeItem.setData(data, forType: NSPasteboard.PasteboardType(type))
            }
            return nativeItem
        }
        return pasteboard.writeObjects(nativeItems)
    }

    private func postShortcut(keyCode: CGKeyCode) throws {
        guard
            let source = CGEventSource(stateID: .hidSystemState),
            let keyDown = CGEvent(keyboardEventSource: source, virtualKey: keyCode, keyDown: true),
            let keyUp = CGEvent(keyboardEventSource: source, virtualKey: keyCode, keyDown: false)
        else {
            throw PlatformOperationError.eventCreationFailed
        }
        keyDown.flags = .maskCommand
        keyUp.flags = .maskCommand
        keyDown.post(tap: .cghidEventTap)
        keyUp.post(tap: .cghidEventTap)
    }
}

private enum PlatformOperationError: Error {
    case eventCreationFailed
}
