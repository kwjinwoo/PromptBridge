import Foundation

/// One native pasteboard item with every representation captured in memory.
public struct PasteboardItem: Equatable, Sendable {
    /// Data keyed by the platform pasteboard type identifier.
    public let representations: [String: Data]

    /// Creates an item from all representations available during capture.
    public init(representations: [String: Data]) {
        self.representations = representations
    }
}

/// Complete in-memory clipboard content captured before synthetic copy.
public struct ClipboardSnapshot: Equatable, Sendable {
    /// Pasteboard items in their original order.
    public let items: [PasteboardItem]

    /// Creates a complete clipboard snapshot.
    public init(items: [PasteboardItem]) {
        self.items = items
    }
}

/// Identity required to prove that automatic paste still targets the captured editor.
public struct TargetContext: Equatable, Sendable {
    /// Process identifier of the active application.
    public let applicationPID: Int32

    /// Stable hash of the focused Accessibility element for the active request.
    public let focusedElementID: Int

    /// Creates a captured application and focused-element identity.
    public init(applicationPID: Int32, focusedElementID: Int) {
        self.applicationPID = applicationPID
        self.focusedElementID = focusedElementID
    }
}

/// Selected source plus the clipboard and focus ownership captured with it.
public struct CapturedSelection: Equatable, Sendable {
    /// Selected source text copied by the hotkey workflow.
    public let source: String

    /// Application and focused editor identity captured before transformation.
    public let context: TargetContext

    /// Pasteboard change count owned by the copied source.
    public let clipboardChangeCount: Int

    /// Creates a captured selection.
    public init(source: String, context: TargetContext, clipboardChangeCount: Int) {
        self.source = source
        self.context = context
        self.clipboardChangeCount = clipboardChangeCount
    }
}

/// Result of replacing clipboard contents for a potential automatic paste.
public struct ClipboardWriteResult: Equatable, Sendable {
    /// Whether the transformed text was written successfully.
    public let succeeded: Bool

    /// Pasteboard generation owned by the attempted write, including a failed write.
    public let changeCount: Int

    /// Creates an owned clipboard-write result.
    public init(succeeded: Bool, changeCount: Int) {
        self.succeeded = succeeded
        self.changeCount = changeCount
    }
}

/// Capture failures that must leave the selected source unchanged.
public enum CaptureError: Error, Equatable, Sendable {
    /// Synthetic copy did not update the clipboard within its bound.
    case copyTimedOut

    /// The copied selection did not contain plain text.
    case noTextSelection

    /// The active application or focused Accessibility element was unavailable.
    case contextUnavailable
}

/// Failure boundaries returned by the local Python prompt pipeline.
public enum EngineFailure: String, Codable, Equatable, Sendable {
    /// Local model process, availability, response, or timeout failure.
    case runtime

    /// Protected placeholders could not be restored safely.
    case restoration

    /// Deterministic preservation checks failed.
    case validation
}

/// Structured local prompt-engine output consumed by the replacement coordinator.
public struct EngineResult: Codable, Equatable, Sendable {
    /// Transformed text, present only when automatic application is safe.
    public let text: String?

    /// Whether deterministic checks allow automatic application.
    public let safeToApply: Bool

    /// Structured failure boundary for a non-applying result.
    public let failureKind: EngineFailure?

    /// Creates a structured engine result.
    public init(text: String?, safeToApply: Bool, failureKind: EngineFailure?) {
        self.text = text
        self.safeToApply = safeToApply
        self.failureKind = failureKind
    }

    /// Creates a safe transformation result.
    public static func success(_ text: String) -> EngineResult {
        EngineResult(text: text, safeToApply: true, failureKind: nil)
    }

    /// Creates a fail-closed transformation result.
    public static func failure(_ kind: EngineFailure) -> EngineResult {
        EngineResult(text: nil, safeToApply: false, failureKind: kind)
    }

    private enum CodingKeys: String, CodingKey {
        case text
        case safeToApply = "safe_to_apply"
        case failureKind = "failure_kind"
    }
}

/// Local transformation boundary used by the macOS coordinator.
public protocol PromptEngine: Sendable {
    /// Transforms selected source without persisting it.
    func transform(_ source: String) async -> EngineResult
}

/// Platform operations whose ownership and timing are verified by the coordinator.
public protocol SelectionSystem: Sendable {
    /// Whether synthetic copy/paste and focused-element checks are authorized.
    var hasAccessibilityPermission: Bool { get }

    /// Current pasteboard generation used to avoid overwriting a newer user copy.
    var clipboardChangeCount: Int { get }

    /// Captures every available representation before PromptBridge changes the clipboard.
    func captureClipboard() -> ClipboardSnapshot

    /// Copies and reads the selected source within a bounded interval.
    func captureSelection(copyTimeout: TimeInterval) throws -> CapturedSelection

    /// Returns the application and focused element that would receive a paste now.
    func currentTargetContext() throws -> TargetContext

    /// Writes validated text and reports success plus the generation owned by the attempt.
    func writeForPaste(_ text: String) -> ClipboardWriteResult

    /// Sends one synthetic paste event to the unchanged target.
    func paste() throws

    /// Restores a snapshot only when the caller still owns the current pasteboard generation.
    @discardableResult
    func restoreClipboard(
        _ snapshot: ClipboardSnapshot,
        ifChangeCount expected: Int
    ) -> Bool
}

/// Observable outcomes of one hotkey invocation without including prompt content.
public enum ReplacementOutcome: Equatable, Sendable {
    /// Validated text was pasted; the associated value reports clipboard restoration.
    case applied(clipboardRestored: Bool)

    /// Accessibility permission is absent, so no capture or paste was attempted.
    case permissionDenied

    /// Selection copy timed out or did not produce safe text and context.
    case captureFailed

    /// Local runtime execution or its timeout failed.
    case runtimeFailure

    /// Restoration or validation blocked automatic application.
    case validationFailure

    /// The active application or focused editor changed during transformation.
    case contextChanged

    /// The user changed the clipboard while the request was active.
    case clipboardChanged

    /// A second hotkey invocation was rejected while one request was active.
    case concurrentInvocation

    /// The validated result could not be written or pasted.
    case pasteFailed
}

/// Serializes hotkey requests and enforces focus and clipboard ownership before paste.
public actor ReplacementCoordinator {
    private let system: any SelectionSystem
    private let engine: any PromptEngine
    private let copyTimeout: TimeInterval
    private var isActive = false

    /// Creates a coordinator around testable platform and engine boundaries.
    public init(
        system: any SelectionSystem,
        engine: any PromptEngine,
        copyTimeout: TimeInterval = 0.75
    ) {
        self.system = system
        self.engine = engine
        self.copyTimeout = copyTimeout
    }

    /// Runs one fail-closed selection-to-replacement workflow.
    public func invoke() async -> ReplacementOutcome {
        guard !isActive else {
            return .concurrentInvocation
        }
        isActive = true
        defer { isActive = false }

        guard system.hasAccessibilityPermission else {
            return .permissionDenied
        }
        let originalClipboard = system.captureClipboard()
        let selection: CapturedSelection
        do {
            selection = try system.captureSelection(copyTimeout: copyTimeout)
        } catch {
            return .captureFailed
        }

        let result = await engine.transform(selection.source)
        guard result.safeToApply, let transformed = result.text else {
            return restore(
                originalClipboard,
                ifChangeCount: selection.clipboardChangeCount,
                returning: result.failureKind == .runtime ? .runtimeFailure : .validationFailure
            )
        }

        guard system.clipboardChangeCount == selection.clipboardChangeCount else {
            return .clipboardChanged
        }
        guard currentContextMatches(selection.context) else {
            return restore(
                originalClipboard,
                ifChangeCount: selection.clipboardChangeCount,
                returning: .contextChanged
            )
        }

        return apply(transformed, selection: selection, restoring: originalClipboard)
    }

    private func apply(
        _ transformed: String,
        selection: CapturedSelection,
        restoring originalClipboard: ClipboardSnapshot
    ) -> ReplacementOutcome {
        let writeResult = system.writeForPaste(transformed)
        guard writeResult.succeeded else {
            return restore(
                originalClipboard,
                ifChangeCount: writeResult.changeCount,
                returning: .pasteFailed
            )
        }
        guard currentContextMatches(selection.context) else {
            return restore(
                originalClipboard,
                ifChangeCount: writeResult.changeCount,
                returning: .contextChanged
            )
        }
        do {
            try system.paste()
            let restored = system.restoreClipboard(
                originalClipboard,
                ifChangeCount: writeResult.changeCount
            )
            return .applied(clipboardRestored: restored)
        } catch {
            system.restoreClipboard(
                originalClipboard,
                ifChangeCount: writeResult.changeCount
            )
            return .pasteFailed
        }
    }

    private func currentContextMatches(_ captured: TargetContext) -> Bool {
        (try? system.currentTargetContext()) == captured
    }

    private func restore(
        _ snapshot: ClipboardSnapshot,
        ifChangeCount expected: Int,
        returning outcome: ReplacementOutcome
    ) -> ReplacementOutcome {
        system.restoreClipboard(snapshot, ifChangeCount: expected)
        return outcome
    }
}
