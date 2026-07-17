import Foundation
import PromptBridgeCore

/// Failures at the short-lived subprocess boundary used by the Phase 3 prototype.
public enum ProcessBridgeError: Error, Sendable {
    /// The Python bridge exceeded the configured local inference bound.
    case timedOut

    /// The subprocess could not be launched or returned unusable output.
    case invalidOutput
}

/// Synchronous subprocess operation injected to keep engine tests deterministic.
public typealias PipelineRunner = @Sendable (String, TimeInterval) throws -> Data

/// Invokes the Python preservation pipeline with source text on standard input.
public struct ProcessPromptEngine: PromptEngine {
    private let timeout: TimeInterval
    private let runner: PipelineRunner

    /// Creates an engine with an injectable subprocess boundary.
    public init(timeout: TimeInterval = 10, runner: @escaping PipelineRunner) {
        self.timeout = timeout
        self.runner = runner
    }

    /// Creates the repository-local Phase 3 Python bridge.
    public init(
        timeout: TimeInterval = 10,
        repositoryDirectory: URL = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
    ) {
        self.init(timeout: timeout) { source, requestTimeout in
            try Self.runPipeline(
                source: source,
                timeout: requestTimeout,
                repositoryDirectory: repositoryDirectory
            )
        }
    }

    /// Returns a decoded pipeline result or a sanitized runtime failure.
    public func transform(_ source: String) async -> EngineResult {
        do {
            let data = try runner(source, timeout)
            let result = try JSONDecoder().decode(EngineResult.self, from: data)
            if result.safeToApply {
                return result.text == nil ? .failure(.runtime) : result
            }
            return result.failureKind == nil ? .failure(.runtime) : result
        } catch {
            return .failure(.runtime)
        }
    }

    private static func runPipeline(
        source: String,
        timeout: TimeInterval,
        repositoryDirectory: URL
    ) throws -> Data {
        let process = Process()
        let input = Pipe()
        let output = Pipe()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        process.arguments = [
            "uv", "run", "--frozen", "python", "-m", "promptbridge.cli",
            "--timeout", String(timeout)
        ]
        process.currentDirectoryURL = repositoryDirectory
        var environment = ProcessInfo.processInfo.environment
        environment["PYTHONPATH"] = repositoryDirectory.appendingPathComponent("src").path
        process.environment = environment
        process.standardInput = input
        process.standardOutput = output
        process.standardError = FileHandle.nullDevice

        do {
            try process.run()
            try input.fileHandleForWriting.write(contentsOf: Data(source.utf8))
            try input.fileHandleForWriting.close()
        } catch {
            process.terminate()
            throw ProcessBridgeError.invalidOutput
        }

        let deadline = Date().addingTimeInterval(timeout + 1)
        while process.isRunning, Date() < deadline {
            Thread.sleep(forTimeInterval: 0.01)
        }
        guard !process.isRunning else {
            process.terminate()
            throw ProcessBridgeError.timedOut
        }
        let data = output.fileHandleForReading.readDataToEndOfFile()
        guard !data.isEmpty else {
            throw ProcessBridgeError.invalidOutput
        }
        return data
    }
}
