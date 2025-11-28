package org.yamcs.mrt.astra;

import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.yamcs.commanding.PreparedCommand;

public class RadiosLink extends AstraSubLink {

	@Override
	public boolean sendCommand(PreparedCommand preparedCommand) {
		// TODO Auto-generated method stub
		throw new UnsupportedOperationException("Unimplemented method 'sendCommand'");
	}

	@Override
	public void handleMqttMessage(MqttMessage message) {
		// TODO Auto-generated method stub
		log.info("Handling MQTT message " + message);
		// throw new UnsupportedOperationException("Unimplemented method
		// 'handleMqttMessage'");
	}

}
