import Carbon
import Foundation
import PromptBridgeCore
import PromptBridgePlatform

let repositoryDirectory = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let system = MacOSSelectionSystem()
let engine = ProcessPromptEngine(repositoryDirectory: repositoryDirectory)
let coordinator = ReplacementCoordinator(system: system, engine: engine)
let hotKey = GlobalHotKey {
    Task {
        let outcome = await coordinator.invoke()
        print("PromptBridge: \(outcome.statusMessage)")
    }
}

do {
    try hotKey.register()
    print("PromptBridge hotkey prototype ready: Command-Option-T")
    if !system.hasAccessibilityPermission {
        system.requestAccessibilityPermission()
        print("PromptBridge: Accessibility permission required; automatic paste is disabled.")
    }
    while true {
        var event: EventRef?
        let receiveStatus = ReceiveNextEvent(
            0,
            nil,
            -1.0,
            true,
            &event
        )
        guard receiveStatus == noErr, let event else {
            continue
        }
        SendEventToEventTarget(event, GetEventDispatcherTarget())
        ReleaseEvent(event)
    }
} catch {
    fputs("PromptBridge: global hotkey registration failed.\n", stderr)
    exit(1)
}

private extension ReplacementOutcome {
    var statusMessage: String {
        switch self {
        case let .applied(clipboardRestored):
            clipboardRestored ? "replacement applied" : "replacement applied; newer clipboard kept"
        case .permissionDenied:
            "Accessibility permission required; source kept"
        case .captureFailed:
            "selection capture failed; source kept"
        case .runtimeFailure:
            "local runtime failed; source kept"
        case .validationFailure:
            "preservation validation failed; source kept"
        case .contextChanged:
            "target context changed; automatic paste stopped"
        case .clipboardChanged:
            "clipboard changed; automatic paste stopped"
        case .concurrentInvocation:
            "another request is active"
        case .pasteFailed:
            "paste failed; source kept"
        }
    }
}
