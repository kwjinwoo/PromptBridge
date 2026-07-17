// swift-tools-version: 6.1

import PackageDescription

let package = Package(
    name: "PromptBridge",
    platforms: [.macOS(.v13)],
    products: [
        .library(name: "PromptBridgeCore", targets: ["PromptBridgeCore"]),
        .executable(name: "promptbridge-hotkey", targets: ["PromptBridgeHotkey"])
    ],
    targets: [
        .target(name: "PromptBridgeCore"),
        .target(
            name: "PromptBridgePlatform",
            dependencies: ["PromptBridgeCore"]
        ),
        .executableTarget(
            name: "PromptBridgeHotkey",
            dependencies: ["PromptBridgeCore", "PromptBridgePlatform"]
        ),
        .testTarget(
            name: "PromptBridgeCoreTests",
            dependencies: ["PromptBridgeCore"],
            path: "swift-tests/PromptBridgeCoreTests"
        ),
        .testTarget(
            name: "PromptBridgePlatformTests",
            dependencies: ["PromptBridgeCore", "PromptBridgePlatform"],
            path: "swift-tests/PromptBridgePlatformTests"
        )
    ]
)
