package org.yamcs.mrt;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import org.eclipse.paho.client.mqttv3.*;
import org.yamcs.*;
import org.yamcs.management.LinkManager;
import org.yamcs.tctm.*;

public class AstraDataLink extends AbstractLink implements AggregatedDataLink {
	private final Map<String, MqttTmLink> subLinksMap = new ConcurrentHashMap<>();
	private List<Link> subLinks = new ArrayList<>();
	private String instance;
	private String name;
	private YConfiguration config;
	private String detailedStatus;

	private MqttAsyncClient client;
	private MqttConnectOptions connOpts;

	@Override
	public void init(String instance, String name, YConfiguration config) throws ConfigurationException {
		super.init(instance, name, config);
		this.instance = instance;
		this.name = name;
		this.config = config;

		this.detailedStatus = "Not started.";

		connOpts = MqttUtils.getConnectionOptions(config);
		client = MqttUtils.newClient(config);

	}

	@Override
	public Spec getSpec() {
		var spec = getDefaultSpec();
		MqttUtils.addConnectionOptionsToSpec(spec);
		return spec;
	}

	@Override
	protected void doStart() {
		try {
			client.setCallback(new MqttCallback() {
				@Override
				public void connectionLost(Throwable cause) {
					eventProducer.sendWarning("MQTT connection lost: " + cause.getMessage());
				}

				@Override
				public void messageArrived(String topic, MqttMessage message) {
					if (!topic.startsWith("radio-"))
						return;

					subLinksMap.computeIfAbsent(topic, t -> {
						eventProducer.sendInfo("Discovered new radio topic: " + t);
						return createSubLinkForTopic(t);
					});

					MqttTmLink radioLink = subLinksMap.get(topic);

					// TODO: forward data to the appropriate sublink, e.g.
					// radioLink.processMqttMessage(message)
				}

				@Override
				public void deliveryComplete(IMqttDeliveryToken token) {
				}
			});

			client.connect(connOpts).waitForCompletion();
			client.subscribe("#", 0).waitForCompletion();

			detailedStatus = "Connected to MQTT broker, listening for topics starting with 'radio-'";
			eventProducer.sendInfo(detailedStatus);
			notifyStarted();

		} catch (Exception e) {
			detailedStatus = "Failed to start AstraDataLink: " + e.getMessage();
			eventProducer.sendWarning(detailedStatus);
			notifyFailed(e);
		}
	}

	private MqttTmLink createSubLinkForTopic(String topic) {
		// You probably want a specialized sublink type instead of LabJackDataLink
		MqttTmLink link = new MqttTmLink();
		String linkName = this.name + "/" + topic;

		link.init(instance, linkName, config);
		link.setParent(this);
		subLinks.add(link);

		LinkManager linkManager = YamcsServer.getServer().getInstance(instance).getLinkManager();
		linkManager.configureDataLink(link, config);

		return link;
	}

	@Override
	protected void doStop() {
		try {
			client.disconnect().waitForCompletion();
		} catch (Exception e) {
			eventProducer.sendWarning("Error disconnecting MQTT: " + e.getMessage());
		}
		notifyStopped();
	}

	@Override
	public List<Link> getSubLinks() {
		return subLinks;
	}

	@Override
	protected Status connectionStatus() {
		return client.isConnected() ? Status.OK : Status.UNAVAIL;
	}

	@Override
	public String getDetailedStatus() {
		return detailedStatus;
	}
}
