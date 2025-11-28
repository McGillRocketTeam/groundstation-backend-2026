package org.yamcs.mrt.astra;

import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.yamcs.ConfigurationException;
import org.yamcs.YConfiguration;
import org.yamcs.tctm.AbstractTcTmParamLink;
import org.yamcs.tctm.Link;

public abstract class AstraSubLink extends AbstractTcTmParamLink implements Link {
	private Status status = Status.UNAVAIL;
	private String detailedStatus = "";

	public void init(String instance, String name, YConfiguration config, Status status, String detailedStatus)
			throws ConfigurationException {

		this.detailedStatus = detailedStatus;
		this.status = status;
		super.init(instance, name, config);
	}

	@Override
	public String getDetailedStatus() {
		return detailedStatus;
	}

	public void setDetailedStatus(String detailedStatus) {
		this.detailedStatus = detailedStatus;
	}

	public abstract void handleMqttMessage(MqttMessage message);;

	@Override
	protected Status connectionStatus() {
		return status;
	}

	@Override
	protected void doStart() {
		notifyStarted();
	}

	@Override
	protected void doDisable() throws Exception {
		this.detailedStatus = "Device disconnected or stopped.";
		super.doDisable();
	}

	@Override
	protected void doStop() {
		notifyStopped();
	}
}
