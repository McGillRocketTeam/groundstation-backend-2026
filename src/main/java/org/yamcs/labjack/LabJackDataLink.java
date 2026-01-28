package org.yamcs.labjack;

import org.yamcs.ConfigurationException;
import org.yamcs.YConfiguration;
import org.yamcs.commanding.PreparedCommand;
import org.yamcs.tctm.AbstractTcTmParamLink;

import com.labjack.LJM;
import com.sun.jna.ptr.IntByReference;

public class LabJackDataLink extends AbstractTcTmParamLink {
	private boolean isConnected = false;
	private int deviceHandle = 0;

	private void attemptLabJackConnection() {
		IntByReference handleRef = new IntByReference(0);
		try {
			LJM.openS("T7", "ANY", "ANY", handleRef);
			log.info("LabJack Connected");
			deviceHandle = handleRef.getValue();
		} catch (Exception E) {
			log.warn("Could not connect to LabJack");
		}
	}

	/**
	 * Reads all readable LabJack pins (analog, digital) and packs the readings into
	 * a binary packet according to
	 * LABJ_XTCE.xml where all analog data is in the most significant bits followed
	 * by all digital data.
	 * This binary packet is then added to the {@link #dataQueue}.
	 */
	private void readAllPins() {
		if (!isConnected) {
			log.error("Attempting to read LabJack pins when no LabJack is connected");
			throw new IllegalStateException();
		}

	}

	@Override
	public void init(String instance, String name, YConfiguration config) throws ConfigurationException {
		super.init(instance, name, config);
		attemptLabJackConnection();
	}

	@Override
	public boolean sendCommand(PreparedCommand preparedCommand) {
		failedCommand(preparedCommand.getCommandId(), "LabJack is not connected.");
		return false;
	}

	@Override
	public String getDetailedStatus() {
		return isConnected ? "LabJack Connected." : "No LabJack Connected.";
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
