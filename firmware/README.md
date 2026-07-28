# Firmware configuration

The repository does not vendor the ArduPilot source tree or unrelated
microcontroller firmware. Project-owned firmware documentation and validated
configuration exports belong under [`ardupilot/`](ardupilot/).

Phase 1 creates the provenance structure only:

```text
firmware/
└── ardupilot/
    ├── README.md
    ├── version.txt
    ├── params/
    │   └── README.md
    └── scripts/
        └── README.md
```

No `.param` file may be created from assumed defaults. Pixhawk and SITL
parameter files will be added only after export from a real, validated
configuration.
