import Foundation
@testable import PromptBridgeCore
@testable import PromptBridgePlatform
import XCTest

final class ProcessPromptEngineTests: XCTestCase {
    func testDecodesSafeStructuredResultFromStandardInputBridge() async {
        let recorder = RunnerRecorder(
            data: Data(
                #"{"text":"Check `parse_item`.","safe_to_apply":true,"failure_kind":null}"#.utf8
            )
        )
        let engine = ProcessPromptEngine(timeout: 3, runner: recorder.run)

        let result = await engine.transform("`parse_item`을 확인해.")

        XCTAssertEqual(result, .success("Check `parse_item`."))
        XCTAssertEqual(recorder.sources, ["`parse_item`을 확인해."])
        XCTAssertEqual(recorder.timeouts, [3])
    }

    func testMalformedOutputAndProcessTimeoutBecomeRuntimeFailure() async {
        let malformed = ProcessPromptEngine { _, _ in Data("not-json".utf8) }
        let timedOut = ProcessPromptEngine { _, _ in throw ProcessBridgeError.timedOut }

        let malformedResult = await malformed.transform("synthetic source")
        let timeoutResult = await timedOut.transform("synthetic source")

        XCTAssertEqual(malformedResult, .failure(.runtime))
        XCTAssertEqual(timeoutResult, .failure(.runtime))
    }

    func testBlockingProcessRunnerStillLetsCoordinatorRejectConcurrentInvocation() async {
        let entered = DispatchSemaphore(value: 0)
        let release = DispatchSemaphore(value: 0)
        let response = Data(
            #"{"text":"Check it.","safe_to_apply":true,"failure_kind":null}"#.utf8
        )
        let engine = ProcessPromptEngine { _, _ in
            entered.signal()
            release.wait()
            return response
        }
        let system = PlatformFakeSelectionSystem()
        let coordinator = ReplacementCoordinator(system: system, engine: engine)

        let first = Task { await coordinator.invoke() }
        XCTAssertEqual(entered.wait(timeout: .now() + 1), .success)
        let second = Task { await coordinator.invoke() }
        try? await Task.sleep(for: .milliseconds(50))
        release.signal()
        try? await Task.sleep(for: .milliseconds(50))
        release.signal()

        let firstOutcome = await first.value
        let secondOutcome = await second.value
        XCTAssertEqual(firstOutcome, .applied(clipboardRestored: true))
        XCTAssertEqual(secondOutcome, .concurrentInvocation)
    }
}

private final class RunnerRecorder: @unchecked Sendable {
    private let data: Data
    private(set) var sources: [String] = []
    private(set) var timeouts: [TimeInterval] = []

    init(data: Data) {
        self.data = data
    }

    func run(source: String, timeout: TimeInterval) throws -> Data {
        sources.append(source)
        timeouts.append(timeout)
        return data
    }
}

private final class PlatformFakeSelectionSystem: SelectionSystem, @unchecked Sendable {
    var hasAccessibilityPermission = true
    private var changeCount = 1

    var clipboardChangeCount: Int {
        changeCount
    }

    func captureClipboard() -> ClipboardSnapshot {
        ClipboardSnapshot(items: [])
    }

    func captureSelection(copyTimeout _: TimeInterval) throws -> CapturedSelection {
        changeCount += 1
        return CapturedSelection(
            source: "synthetic source",
            context: TargetContext(applicationPID: 1, focusedElementID: 1),
            clipboardChangeCount: changeCount
        )
    }

    func currentTargetContext() throws -> TargetContext {
        TargetContext(applicationPID: 1, focusedElementID: 1)
    }

    func writeForPaste(_: String) -> ClipboardWriteResult {
        changeCount += 1
        return ClipboardWriteResult(succeeded: true, changeCount: changeCount)
    }

    func paste() throws {}

    func restoreClipboard(_: ClipboardSnapshot, ifChangeCount expected: Int) -> Bool {
        guard expected == changeCount else {
            return false
        }
        changeCount += 1
        return true
    }
}
