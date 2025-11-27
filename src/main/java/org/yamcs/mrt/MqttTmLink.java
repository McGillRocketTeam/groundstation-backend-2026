package org.yamcs.mrt;

import org.yamcs.ConfigurationException;
import org.yamcs.YConfiguration;
import org.yamcs.commanding.PreparedCommand;
import org.yamcs.tctm.AbstractTcTmParamLink;

public class MqttTmLink extends AbstractTcTmParamLink {

	@Override
	public void init(String instance, String name, YConfiguration config) throws ConfigurationException {
		super.init(instance, name, config);
	}

	@Override
	public boolean sendCommand(PreparedCommand preparedCommand) {
		failedCommand(preparedCommand.getCommandId(), "Radio is not connected.");
		return false;
	}

	@Override
	public String getDetailedStatus() {
		return "Radio connected, listening on 435Mhz.";
	}

	@Override
	protected Status connectionStatus() {
		// TODO Auto-generated method stub
		return Status.UNAVAIL;
	}

	@Override
	protected void doStart() {
		if (isDisabled()) {
			notifyStarted();
		} else {
			notifyStarted();
		}
	}

	@Override
	protected void doStop() {
		notifyStopped();
	}

	@Override
	public boolean isTmPacketDataLinkImplemented() {
		return false;
	}
}
