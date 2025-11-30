<p align="center">
    <img width="595.5" height="101.25" src="assets/logo.svg">
</p>

---

# Ground Station Frontend 2026

> [!NOTE]  
> The information or structure of this repository is subject to change
> as planning continues.

This project is based off of the offical [YAMCS MQTT repository](https://github.com/yamcs/yamcs-mqtt).

## Documentation

[https://docs.yamcs.org/yamcs-maven-plugin/](https://docs.yamcs.org/yamcs-maven-plugin/)

### Prerequisites

- Java 17+ and Maven
- Local MQTT Broker (optional)

### Running

1. **Start Yamcs**:

   ```bash
   mvn yamcs:run
   ```

2. You can also start Yamcs by opening the project in IntelliJ Idea and adding
   a new Maven run target with the command `yamcs:run`

You can navigate now to [http://localhost:8090/](http://localhost:8090/).

### Configuration

This setup uses either a local MQTT broker, or a cloud hosted one. To configure
the MQTT broker, change the "brokers" configuration line in `src/main/yamcs/etc/yamcs.ground_station.yaml`.
