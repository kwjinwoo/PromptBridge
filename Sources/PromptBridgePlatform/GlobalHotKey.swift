import Carbon
import Foundation

/// Errors returned when the prototype cannot install its one global hotkey.
public enum GlobalHotKeyError: Error, Sendable {
    /// Carbon rejected event-handler or hotkey registration.
    case registrationFailed(OSStatus)
}

/// Owns one Command-Option-T Carbon hotkey for the process lifetime.
public final class GlobalHotKey: @unchecked Sendable {
    private let callback: @Sendable () -> Void
    private var eventHandler: EventHandlerRef?
    private var hotKey: EventHotKeyRef?

    /// Creates the Phase 3 hotkey registration.
    public init(callback: @escaping @Sendable () -> Void) {
        self.callback = callback
    }

    deinit {
        if let hotKey {
            UnregisterEventHotKey(hotKey)
        }
        if let eventHandler {
            RemoveEventHandler(eventHandler)
        }
    }

    /// Registers Command-Option-T with the application event target.
    public func register() throws {
        var eventType = EventTypeSpec(
            eventClass: OSType(kEventClassKeyboard),
            eventKind: UInt32(kEventHotKeyPressed)
        )
        let handlerStatus = InstallEventHandler(
            GetApplicationEventTarget(),
            promptBridgeHotKeyHandler,
            1,
            &eventType,
            Unmanaged.passUnretained(self).toOpaque(),
            &eventHandler
        )
        guard handlerStatus == noErr else {
            throw GlobalHotKeyError.registrationFailed(handlerStatus)
        }

        let identifier = EventHotKeyID(signature: 0x5042_5247, id: 1)
        let hotKeyStatus = RegisterEventHotKey(
            17,
            UInt32(cmdKey | optionKey),
            identifier,
            GetApplicationEventTarget(),
            0,
            &hotKey
        )
        guard hotKeyStatus == noErr else {
            throw GlobalHotKeyError.registrationFailed(hotKeyStatus)
        }
    }

    fileprivate func invoke() {
        callback()
    }
}

private let promptBridgeHotKeyHandler: EventHandlerUPP = { _, _, userData in
    guard let userData else {
        return OSStatus(eventNotHandledErr)
    }
    let hotKey = Unmanaged<GlobalHotKey>.fromOpaque(userData).takeUnretainedValue()
    hotKey.invoke()
    return noErr
}
