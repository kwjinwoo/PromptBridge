import Foundation
@testable import PromptBridgeCore
import XCTest

final class ReplacementCoordinatorTests: XCTestCase {
    func testSuccessfulFlowPastesValidatedTextAndRestoresEveryClipboardRepresentation() async {
        let snapshot = ClipboardSnapshot(items: [
            PasteboardItem(representations: [
                "public.utf8-plain-text": Data("original".utf8),
                "public.rtf": Data([0x7B, 0x5C, 0x72, 0x74, 0x66])
            ])
        ])
        let system = FakeSelectionSystem(snapshot: snapshot)
        let coordinator = ReplacementCoordinator(
            system: system,
            engine: StubEngine(result: .success("Check `parse_item`."))
        )

        let outcome = await coordinator.invoke()

        XCTAssertEqual(outcome, .applied(clipboardRestored: true))
        XCTAssertEqual(system.pastedTexts, ["Check `parse_item`."])
        XCTAssertEqual(system.restoredSnapshots, [snapshot])
    }

    func testFocusChangePreventsPasteAndRestoresOwnedClipboard() async {
        let system = FakeSelectionSystem()
        let engine = StubEngine { _ in
            system.context = TargetContext(applicationPID: 42, focusedElementID: 99)
            return .success("Check it.")
        }
        let coordinator = ReplacementCoordinator(system: system, engine: engine)

        let outcome = await coordinator.invoke()

        XCTAssertEqual(outcome, .contextChanged)
        XCTAssertTrue(system.pastedTexts.isEmpty)
        XCTAssertEqual(system.restoredSnapshots.count, 1)
    }

    func testUserClipboardChangePreventsPasteWithoutOverwritingNewClipboard() async {
        let system = FakeSelectionSystem()
        let engine = StubEngine { _ in
            system.simulateUserClipboardChange()
            return .success("Check it.")
        }
        let coordinator = ReplacementCoordinator(system: system, engine: engine)

        let outcome = await coordinator.invoke()

        XCTAssertEqual(outcome, .clipboardChanged)
        XCTAssertTrue(system.pastedTexts.isEmpty)
        XCTAssertTrue(system.restoredSnapshots.isEmpty)
    }

    func testRuntimeAndValidationFailuresNeverPaste() async {
        for (failure, expected) in [
            (EngineFailure.runtime, ReplacementOutcome.runtimeFailure),
            (EngineFailure.validation, ReplacementOutcome.validationFailure),
            (EngineFailure.restoration, ReplacementOutcome.validationFailure)
        ] {
            let system = FakeSelectionSystem()
            let coordinator = ReplacementCoordinator(
                system: system,
                engine: StubEngine(result: .failure(failure))
            )

            let outcome = await coordinator.invoke()

            XCTAssertEqual(outcome, expected)
            XCTAssertTrue(system.pastedTexts.isEmpty)
            XCTAssertEqual(system.restoredSnapshots.count, 1)
        }
    }

    func testPermissionAndCopyTimeoutFailClosed() async {
        let permissionDenied = FakeSelectionSystem()
        permissionDenied.hasAccessibilityPermission = false
        let deniedCoordinator = ReplacementCoordinator(
            system: permissionDenied,
            engine: StubEngine(result: .success("unused"))
        )

        let deniedOutcome = await deniedCoordinator.invoke()
        XCTAssertEqual(deniedOutcome, .permissionDenied)
        XCTAssertTrue(permissionDenied.pastedTexts.isEmpty)

        let timedOut = FakeSelectionSystem()
        timedOut.captureError = .copyTimedOut
        let timeoutCoordinator = ReplacementCoordinator(
            system: timedOut,
            engine: StubEngine(result: .success("unused"))
        )

        let timeoutOutcome = await timeoutCoordinator.invoke()
        XCTAssertEqual(timeoutOutcome, .captureFailed)
        XCTAssertTrue(timedOut.pastedTexts.isEmpty)
    }

    func testConcurrentInvocationIsRejectedWhileFirstRequestIsTransforming() async {
        let system = FakeSelectionSystem()
        let gate = AsyncGate()
        let engine = StubEngine { _ in
            await gate.wait()
            return .success("Check it.")
        }
        let coordinator = ReplacementCoordinator(system: system, engine: engine)

        let first = Task { await coordinator.invoke() }
        await gate.waitUntilEntered()
        let second = await coordinator.invoke()
        await gate.open()

        let firstOutcome = await first.value
        XCTAssertEqual(second, .concurrentInvocation)
        XCTAssertEqual(firstOutcome, .applied(clipboardRestored: true))
        XCTAssertEqual(system.pastedTexts.count, 1)
    }

    func testPasteFailureDoesNotOverwriteClipboardChangedAfterPromptBridgeWrite() async {
        let system = FakeSelectionSystem()
        system.pasteError = true
        system.changeClipboardBeforePasteFailure = true
        let coordinator = ReplacementCoordinator(
            system: system,
            engine: StubEngine(result: .success("Check it."))
        )

        let outcome = await coordinator.invoke()

        XCTAssertEqual(outcome, .pasteFailed)
        XCTAssertTrue(system.restoredSnapshots.isEmpty)
    }

    func testClipboardWriteFailureRestoresUsingGenerationOwnedByFailedWrite() async {
        let system = FakeSelectionSystem()
        system.writeError = true
        system.changeClipboardBeforeWriteFailure = true
        let coordinator = ReplacementCoordinator(
            system: system,
            engine: StubEngine(result: .success("Check it."))
        )

        let outcome = await coordinator.invoke()

        XCTAssertEqual(outcome, .pasteFailed)
        XCTAssertEqual(system.restoredSnapshots.count, 1)
        XCTAssertTrue(system.pastedTexts.isEmpty)
    }

    func testFocusChangeDuringClipboardWriteStillPreventsPaste() async {
        let system = FakeSelectionSystem()
        system.contextChangeDuringWrite = true
        let coordinator = ReplacementCoordinator(
            system: system,
            engine: StubEngine(result: .success("Check it."))
        )

        let outcome = await coordinator.invoke()

        XCTAssertEqual(outcome, .contextChanged)
        XCTAssertTrue(system.pastedTexts.isEmpty)
        XCTAssertEqual(system.restoredSnapshots.count, 1)
    }
}

private struct StubEngine: PromptEngine {
    let operation: @Sendable (String) async -> EngineResult

    init(result: EngineResult) {
        operation = { _ in result }
    }

    init(operation: @escaping @Sendable (String) async -> EngineResult) {
        self.operation = operation
    }

    func transform(_ source: String) async -> EngineResult {
        await operation(source)
    }
}

private final class FakeSelectionSystem: SelectionSystem, @unchecked Sendable {
    var hasAccessibilityPermission = true
    var context = TargetContext(applicationPID: 42, focusedElementID: 7)
    var captureError: CaptureError?
    var pasteError = false
    var changeClipboardBeforePasteFailure = false
    var writeError = false
    var changeClipboardBeforeWriteFailure = false
    var contextChangeDuringWrite = false
    private(set) var pastedTexts: [String] = []
    private(set) var restoredSnapshots: [ClipboardSnapshot] = []

    private let snapshot: ClipboardSnapshot
    private var changeCount = 10
    private var pasteText: String?

    init(snapshot: ClipboardSnapshot = ClipboardSnapshot(items: [])) {
        self.snapshot = snapshot
    }

    var clipboardChangeCount: Int {
        changeCount
    }

    func captureClipboard() -> ClipboardSnapshot {
        snapshot
    }

    func captureSelection(copyTimeout _: TimeInterval) throws -> CapturedSelection {
        if let captureError {
            throw captureError
        }
        changeCount += 1
        return CapturedSelection(
            source: "`parse_item`을 확인해.",
            context: context,
            clipboardChangeCount: changeCount
        )
    }

    func currentTargetContext() throws -> TargetContext {
        context
    }

    func writeForPaste(_ text: String) -> ClipboardWriteResult {
        if writeError {
            if changeClipboardBeforeWriteFailure {
                simulateUserClipboardChange()
            }
            return ClipboardWriteResult(succeeded: false, changeCount: changeCount)
        }
        pasteText = text
        changeCount += 1
        if contextChangeDuringWrite {
            context = TargetContext(applicationPID: 42, focusedElementID: 99)
        }
        return ClipboardWriteResult(succeeded: true, changeCount: changeCount)
    }

    func paste() throws {
        if pasteError {
            if changeClipboardBeforePasteFailure {
                simulateUserClipboardChange()
            }
            throw SyntheticError.pasteFailed
        }
        if let pasteText {
            pastedTexts.append(pasteText)
        }
    }

    func restoreClipboard(_ snapshot: ClipboardSnapshot, ifChangeCount expected: Int) -> Bool {
        guard changeCount == expected else {
            return false
        }
        restoredSnapshots.append(snapshot)
        changeCount += 1
        return true
    }

    func simulateUserClipboardChange() {
        changeCount += 1
    }
}

private enum SyntheticError: Error {
    case pasteFailed
}

private actor AsyncGate {
    private var entered = false
    private var continuation: CheckedContinuation<Void, Never>?

    func wait() async {
        entered = true
        await withCheckedContinuation { continuation = $0 }
    }

    func waitUntilEntered() async {
        while !entered {
            await Task.yield()
        }
    }

    func open() {
        continuation?.resume()
        continuation = nil
    }
}
