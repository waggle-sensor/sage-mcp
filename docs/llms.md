---
sidebar_label: Overview
sidebar_position: 1
---

# Sage: A distributed software-defined sensor network.

## What is Sage?


Geographically distributed sensor systems that include cameras, microphones, and weather and air quality stations can generate such large volumes of data that fast and efficient analysis is best performed by an embedded computer connected directly to the sensor. Sage is exploring new techniques for applying machine learning algorithms to data from such intelligent sensors and then building reusable software that can run programs within the embedded computer and transmit the results over the network to central computer servers. Distributed, intelligent sensor networks that can collect and analyze data are an essential tool for scientists seeking to understand the impacts of global urbanization, natural disasters such as flooding and wildfires, and changes on natural ecosystems and city infrastructure.

Sage is deploying sensor nodes that support machine learning frameworks in environmental testbeds in California, Colorado, and Kansas and in urban environments in Illinois and Texas. The reusable cyberinfrastructure running on these testbeds will give scientists new data for building models to study these coupled systems. The software components developed are open source and provide an open architecture to enable scientists from a wide range of fields to build their own intelligent sensor networks.

Partners are deploying testbeds in Australia, Japan, UK, and Taiwan, providing scientists with even more data for analysis. The toolkit is also extending the current educational curriculum used in Chicago to inspire young people – with an emphasis on women and minorities, to pursue science, technology, and mathematics careers – by providing a platform for students to explore measurement-based science questions related to the natural and built environments.

The data from sensors and applications is hosted in the cloud to facilitate easy data analysis.

![High level overview of Sage](./images/sage-flow.png)

## Who are the users?

The most common users have included:

- Domain scientists interested in developing edge AI applications.
- Users interested in sensor and application-produced datasets.
- Cyberinfrastructure researchers interested in platform research.
- Domain scientists interested in adding new sensors and deploying nodes to answer specific science questions.

## How do I use the platform?

This depends on your desired interaction interest.  The platform consists of edge compute applications which process data (ex. sensor readings, camera images, audio recordings, etc). These edge applications then produce their own data (ex. inferences) and upload the results to a cloud database. This cloud database can be accessed directly and/or additional compute can be performed on the cloud data.

![User Interaction](./images/waggle_interact.png)

The entry-point into learning about your interaction with the system might be best directed by getting answers (by following the links) to the question(s) you are most interested in.

[How do I access sensors?](../tutorials/access-waggle-sensors.md)
- Want to learn about existing, supported sensors?
- Do you have a new sensor that you want to write an edge application for?

[How do I run edge apps?](../tutorials/edge-apps/intro-to-edge-apps)
- Want to know how to create an edge app?
- Want to know how your edge app can get access to edge sensor data?
- Want to share your edge app data with other edge applications?
- Want to know how to upload data to the cloud?

[How do I access and use data?](../tutorials/accessing-data.md)
- Want to learn about how data is stored/organized?
- Do you have data that is up in the cloud and want to know how to access it?

[How do I compute in the cloud?](../tutorials/cloud-compute.md)
- Want to know how to autonomously react to edge produced data?
- Want to know how to trigger an HPC event?
- Want to get a text message when your edge application does something cool?

[How do I build my own device?](../tutorials/create-waggle.md)
- Want to set up your own device for local edge app development?
- Want to teach AI to a classroom of students?

## How is the cyberinfrastructure architected?

If you are interested in learning more about how the cyberinfrastructure works you can head on over to the [Architecture Overview](./architecture.md) page.

---
sidebar_label: Architecture
sidebar_position: 2
---

# Architecture

The cyberinfrastructure consists of coordinating hardware and software services enabling AI at the edge. Below is a quick summary of the different infrastructure pieces, starting at the highest-level and zooming into each component to understand the relationships and role each plays.

## High-Level Infrastructure

![Figure 1: High-level Node & Beehive Relationship](./images/arch_high_01.svg)

There are 2 main components of the cyberinfrastructure:
- [Nodes](#nodes) that exist at the edge
- The cloud that hosts services and storage systems to facilitate running [“science goals”](#science-goals) @ the edge

Every edge node maintains connections to 2 core cloud components: one to a [Beehive](#beehive) and one to a [Beekeeper](#beekeeper)

### Beekeeper

The Beekeeper is an administrative server that allows system administrators to perform actions on the nodes such as gather health metrics and perform software updates.  All nodes "phone home" to their Beekeeper and maintain this "life-line" connection.

> Details & source code: https://github.com/waggle-sensor/beekeeper

### Beehive

The Node-to-Beehive connection is the pipeline for the science. It is over this connection that instructions for the node will be sent, in addition to how data is published into the Beehive storage systems from applications ([plugins](#what-is-a-plugin)) running on the nodes.

The overall infrastructure supports multiple Beehives, where each node is associated with a single Beehive. The set of nodes associated with a Beehive creates a "project" where each "project" is separate, having its own data store, web services, etc.

![Figure 2: Multiple Beehives](./images/arch_beehives_01.svg)

In the example above, there are 2 nodes associated with Beehive 1, while a single node is associated with Beehive 2.  With all nodes, in this example, being administered by a single [Beekeeper](#beekeeper).

> _Note_: the example above shows a single Beekeeper, but a second Beekeeper could have been used for administrative isolation.

> Details & source code: https://github.com/waggle-sensor/waggle-beehive-v2

## Beehive Infrastructure

Looking deeper into the Beehive infrastructure, it contains 2 main components:
- software services such as the [Edge Scheduler (ES)](#edge-scheduler-es), [Lambda Triggers (LT)](#lambda-triggers-lt), data APIs, and websites/portals
- data storage systems such as the [Data Repository (DR)](#data-repository-dr) and the [Edge Code Repository (ECR)](#edge-code-repository-ecr)

![Figure 3: Beehive High-level Architecture](./images/beehive_high_01.svg)

The Beehive is the “command center” for interacting with the Waggle nodes at the edge. Hosting websites and interfaces allowing scientists to create [science goals](#science-goals) to run [plugins](#what-is-a-plugin) at the edge & browse the data produced by those [plugins](#what-is-a-plugin).

![Figure 4: Beehive Infrastructure Details](./images/beehive_details_01.svg)

The software services and data storage systems are deployed within a [kubernetes](https://kubernetes.io/) environment to allow for easy administration and to support running in a multiple server architecture, supporting redundancy and service replication.

While the services running within Beehive are many (both graphical and [REST](https://en.wikipedia.org/wiki/Representational_state_transfer) style API interfaces), the following is an outline of the most vital.

### Data Repository (DR)

The Data Repository is the data store for housing all the edge produced [plugin](#what-is-a-plugin) data. It consists of different storage technologies (i.e. [influxdb](https://www.influxdata.com/)) and techniques to store simple textual data (i.e. key-value pairs) in addition to large blobular data (i.e. audio, images, video). The Data Repository additionally has an API interface for easy access to this data.

The data store is a time-series database of key-value pairs with each entry containing metadata about how and when the data originated @ the edge. Included in this metadata is the data collection timestamp, [plugin](#what-is-a-plugin) version used to collect the data, the [node](#nodes) the [plugin](#what-is-a-plugin) was run on, and the specific compute unit within the node that the [plugin](#what-is-a-plugin) was running on.

```json
{
    "timestamp":"2022-06-10T22:37:47.369013647Z",
    "name":"iio.in_temp_input",
    "value":25050,
    "meta":{
        "host":"0000dca632ed6d06.ws-rpi",
        "job":"sage",
        "node":"000048b02d35a97c",
        "plugin":"plugin-iio:0.6.0",
        "sensor":"bme680",
        "task":"iio-rpi",
        "vsn":"W08C"
    }
}
```

In the above example, the value of `25050` was collected @ `2022-06-10T22:37:47.369013647Z` from the `bme680` sensor on node `000048b02d35a97c` via the `plugin-iio:0.6.0` [plugin](#what-is-a-plugin).

> _Note_: see the [Access and use data](/docs/tutorials/accessing-data) site for more details and data access examples.

> Details & source code: https://github.com/waggle-sensor/data-repository

### Edge Scheduler (ES)

The Edge Scheduler is defined as the suite of services running in Beehive that facilitate running [plugins](#what-is-a-plugin) @ the edge. Included here are user interfaces and APIs for scientists to create and manage their [science goals](#science-goals). The Edge Scheduler continuously analyzes node workloads against all the [science goals](#science-goals) to determine how the [science goals](#science-goals) are deployed to the Beehive nodes. When it is determined that a node's [science goals](#science-goals) are to be updated, the Edge Scheduler interfaces with [WES](#waggle-edge-stack-wes) running on those nodes to update the node's local copy of the [science goals](#science-goals). Essentially, the Edge Scheduler is the overseer of all the Beehive's nodes, deploying [science goals](#science-goals) to them to meet the scientists [plugin](#what-is-a-plugin) execution objectives.

> Details & source code: https://github.com/waggle-sensor/edge-scheduler

### Edge Code Repository (ECR)

The Edge Code Repository is the "app store" that hosts all the tested and benchmarked edge [plugins](#what-is-a-plugin) that can be deployed to the nodes. This is the interface allowing users to discover existing [plugins](#what-is-a-plugin) (for potential inclusion in their [science goals](#science-goals)) in addition to submitting their own. At it's core, the ECR provides a verified and versioned repository of [plugin](#what-is-a-plugin) [Docker](https://www.docker.com) images that are pulled by the nodes when a [plugin](#what-is-a-plugin) is to be downloaded as run-time component of a [science goal](#science-goals).

> Details & source code: https://github.com/waggle-sensor/edge-code-repository

### Lambda Triggers (LT)

The Lambda Triggers service provides a framework for running reactive code within the Beehive. There are two kinds of reaction triggers considered here: From-Edge and To-Edge.

From-Edge triggers, or messages that originate from an edge node, can be used to trigger lambda functions -- for example, if high wind velocity is detected, a function could be triggered to determine how to reconfigure sensors or launch a computation or send an alert.

To-Edge triggers are messages that are to change a node's behavior. For example an HPC calculation or cloud-based data analysis could trigger an [Edge Scheduler](#edge-scheduler-es) API call to request a [science goal](#science-goals) to be run on a particular set of edge nodes.

> Details & source code: https://github.com/waggle-sensor/lambda-triggers

## Nodes

Nodes are the edge computing component of the cyberinfrastructure. All nodes consist of 3 items:
1. **Persisent storage** for housing downloaded [plugins](#what-is-a-plugin) and caching published data before it is transferred to the node's Beehive
2. **CPU and GPU compute modules** where [plugins](#what-is-a-plugin) are executed and perform the accelerated inferences
3. **Sensors** such as environment sensors, cameras and [LiDAR systems](https://en.wikipedia.org/wiki/Lidar)

![Figure 5: Node Overview](./images/node_overview_01.svg)

Edge nodes enable fast computation @ the edge, leveraging the large non-volatile storage to handle caching of high frequency data (including images, audio and video) in the event the node is "offline" from its Beehive.  Through expansion ports the nodes support the adding and removing of sensors to fully customize the node deployments for the particular deployment environment.

Overall, even though the nodes may use different CPU architectures and different sensor configurations, they all leverage the same [Waggle Edge Stack (WES)](#waggle-edge-stack-wes) to run [plugins](#what-is-a-plugin).

### Wild Sage Node (Wild Waggle Node)

The Wild Sage Node (or Wild Waggle Node) is a custom built weather-proof enclosure intended for remote outdoor installation. The node features software and hardware resilience via a [custom operating system](https://github.com/waggle-sensor/wildnode-image) and [custom circuit board](https://github.com/waggle-sensor/wagman). Internal to the node is a power supply and PoE network switch supporting the addition of sensors through standard Ethernet (PoE), USB and other embedded protocols via the node expansion ports.

![Figure 6: Wild Sage/Waggle Node Overview](./images/node_wild_01.svg)

The technical capabilities of these nodes consists of:
- NVidia Xavier NX ARM64 [Node Controller](https://github.com/waggle-sensor/nodecontroller) w/ 8GB of shared CPU/GPU RAM
- 1 TB of NVMe storage
- 4x PoE expansion ports
- 1x USB2 expansion port
- optional [Stevenson Shield](https://en.wikipedia.org/wiki/Stevenson_screen) housing a RPi 4 w/ environmental sensors & microphone
- optional 2nd NVidia Xavier NX ARM64 [Edge Processor](https://github.com/waggle-sensor/edgeprocessor)

> Node installation manual: [https://sagecontinuum.org/docs/installation-manuals/wsn-manual](/docs/installation-manuals/wsn-manual)

> Details & source code: https://github.com/waggle-sensor/wild-waggle-node

### Blade Nodes

A Blade Node is a standard commercially available server intended for use in a climate controlled machine room, or extended temperature range telecom-grade blades for harsher environments. The [AMD64 based operating system](https://github.com/waggle-sensor/blade-image) supports these types of nodes, enabling the services needed to support [WES](#waggle-edge-stack-wes).

![Figure 7: Blade Node Overview](./images/node_blade_01.svg)

The above diagram shows the basic technical configuration of a Blade Node:
- Multi-core ARM64
- 32GB of RAM
- Dedicated NVida T4 GPU
- 1 TB of SSD storage

> _Note_: it is possible to add the same optional [Stevenson Shield](https://en.wikipedia.org/wiki/Stevenson_screen) housing that is available to the [Wild Sage Nodes](#wild-sage-node-wild-waggle-node)

> Details & source code: https://github.com/waggle-sensor/waggle-blade

## Running plugins @ the Edge

Included in the Waggle operating systems are the core components necessary to enable running [plugins](#what-is-a-plugin) @ the edge.  At the heart of this is [k3s](https://k3s.io/), which creates a protected & isolated run-time environment. This environment combined with the tools and services provided by [WES](#waggle-edge-stack-wes) enable [plugin](#what-is-a-plugin) access to the node's CPU, GPU, sensors and cameras.

### Waggle Edge Stack (WES)

The Waggle Edge Stack is the set of core services running within the [edge node's](#nodes) [k3s](https://k3s.io/) run-time environment that supports all the features that [plugins](#what-is-a-plugin) need to run on the Waggle nodes. The WES services coordinate with the core [Beehive](#beehive) services to download & run scheduled [plugins](#what-is-a-plugin) (including load balancing) and facilitate uploading [plugin](#what-is-a-plugin) published data to the Beehive [data repository](#data-repository-dr). Through abstraction technologies and WES provided tools, [plugins](#what-is-a-plugin) have access to sensor and camera data.

![Figure 8: Waggle Edge Stack Overview](./images/wes_overview_01.svg)

The above diagram demonstrates 2 [plugins](#what-is-a-plugin) running on a Waggle node.  Plugin 1 ("neon-kafka") is an example [plugin](#what-is-a-plugin) that is running alongside Plugin 2 ("data-smooth"). In this example, "neon-kafka" (via the WES tools) is reading metrics from the node's sensors and then publishing that data within the WES run-time environment (internal to the node).
At the same time, the "data-smooth" [plugin](#what-is-a-plugin) is subscribing to this data stream, performing some sort of inference and then publishing the inference results (via WES tools) to Beehive.

> _Note_: see the [Edge apps](/docs/category/edge-apps) guide on how to create a Waggle [plugin](#what-is-a-plugin).

> Details & source code: https://github.com/waggle-sensor/waggle-edge-stack

### What is a plugin?

Plugins are the user-developed modules that the cyberinfrastructure is designed around. At it's simplest definition a "plugin" is code that runs @ the edge to perform some task. That task may be simply collecting sample camera images or a complex inference combining sensor data and results published from other plugins. A plugin's code will interface with the edge node's sensor(s) and then publish resulting data via the tools provided by [WES](#waggle-edge-stack-wes). All developed plugins are hosted by the Beehive [Edge Code Repository](#edge-code-repository-ecr).

> See [how to create plugins](/docs/category/edge-apps) for details.

### Science Goals

A "science goal" is a rule-set for how and when [plugins](#what-is-a-plugin) are run on edge nodes. These science goals are created by scientist to accomplish a science objective through the execution of [plugins](#what-is-a-plugin) in a specific manner. Goals are created, in a human language, and managed within the Beehive [Edge Scheduler](#edge-scheduler-es). It is then the cyberinfrastucture responsibility to deploy the science goals to the edge nodes and execute the goal's [plugins](#what-is-a-plugin). The [tutorial](../tutorials/schedule-jobs.md) walks through running a science goal.

## LoRaWAN

[The Waggle Edge Stack](#waggle-edge-stack-wes) includes the [ChirpStack software stack](#chirpstack) and other services to facilitate communication between [Nodes](#nodes) and LoRaWAN devices. This empowers [Nodes](#nodes) to effortlessly establish connections with wireless sensors, enabling your [plugins](#what-is-a-plugin) to seamlessly access and harness valuable data from these sensors.

>To get started using LoRaWAN, head over to the [Contact Us](../contact-us.md) page. A tutorial will be available soon showing you how to get started with LoRaWAN.

<!--To get started with using LoRaWAN, you can follow the step-by-step instructions in the [tutorial](../tutorials/schedule-jobs.md). -->

![Figure 9: WES Lorawan Architecture](./images/arch_wes_lorawan.svg)

The above diagram demonstrates the hardware in [Nodes](#nodes) and services in [WES](#waggle-edge-stack-wes) that enable [Nodes](#nodes) to use LoRaWAN and publish the measurements to a [Beehive](#beehive). The following sections will explain each componenent and service.

>source code:
> - [wes-chirpstack](https://github.com/waggle-sensor/waggle-edge-stack/tree/main/kubernetes/wes-chirpstack)
> - [wes-chirpstack-server](https://github.com/waggle-sensor/wes-chirpstack-server)
> - [wes-rabbitmq](https://github.com/waggle-sensor/waggle-edge-stack/blob/main/kubernetes/wes-rabbitmq.yaml)
> - [Tracker](https://github.com/waggle-sensor/wes-chirpstack-device-tracker)
> - [Lorawan Listener Plugin](https://github.com/FranciscoLozCoding/plugin-lorawan-listener)

### What is LoRaWAN?

LoRaWAN, short for "Long Range Wide Area Network," is a wireless communication protocol designed for low-power, long-range communication between IoT (Internet of Things) devices. It employs a low-power wide-area network (LPWAN) technology, making it ideal for connecting remote sensors and devices. For more information view the documentation [here](https://www.thethingsnetwork.org/docs/lorawan/).

### Chirpstack

ChirpStack is a robust and open-source LoRaWAN Network Server that enables efficient management of LoRaWAN devices, gateways, and data. Its architecture consists of several crucial components, each serving a distinct role in LoRaWAN network operations. Below, we provide a brief overview of these components along with links to ChirpStack documentation for further insights.

>[Chirpstack documentation](https://www.chirpstack.io/docs/index.html)

#### UDP Packet Forwarder

The UDP Packet Forwarder is an essential component that acts as a bridge between LoRa gateways and the [ChirpStack Network Server](#chirpstack-server). It receives incoming packets from LoRa gateways and forwards them to the [ChirpStack Gateway Bridge](#chirpstack-gateway-bridge) for further processing. To learn more about the UDP Packet Forwarder, refer to the documentation [here](https://github.com/RAKWireless/udp-packet-forwarder).

#### ChirpStack Gateway Bridge

The ChirpStack Gateway Bridge is responsible for translating gateway-specific protocols into a standard format for the [ChirpStack Network Server](#chirpstack-server). It connects to a [UDP Packet Forwader](#udp-packet-forwarder), ensuring that data is properly formatted and can be seamlessly processed by the network server. For in-depth information on the ChirpStack Gateway Bridge, explore the documentation [here](https://www.chirpstack.io/docs/chirpstack-gateway-bridge/index.html).

#### MQTT Broker

[WES](#waggle-edge-stack-wes) includes a MQTT (Message Queuing Telemetry Transport) broker to handle communication between various services. MQTT provides a lightweight and efficient messaging system. This service ensures that data flows smoothly between the network server, gateways, and applications. You can find detailed information about the MQTT broker integration in the ChirpStack documentation [here](https://www.chirpstack.io/docs/chirpstack/integrations/mqtt.html).

#### ChirpStack Server
The ChirpStack Server serves as the core component, managing device sessions, data, and application integrations. It utilizes [Redis](https://redis.io/) for device sessions, metrics, and caching, ensuring efficient data handling and retrieval. For persistent data storage, ChirpStack uses [PostgreSQL](https://www.postgresql.org/), accommodating records for tenants, applications, devices, and more. For a comprehensive understanding of the ChirpStack Server and its associated database technologies, consult the ChirpStack documentation [here](https://www.chirpstack.io/docs/chirpstack/requirements.html).

>NOTE: Chirpstack v4 combined the application and network server into one component.

### Tracker
The Tracker is a service designed to record the connectivity of LoRaWAN devices to the [Nodes](#nodes). This service uses the information received from the [MQTT broker](#mqtt-broker) to call [ChirpStack's gRPC API](https://www.chirpstack.io/docs/chirpstack/api/grpc.html). The information received from the API is then used to keep the Node's manifest up-to-date. Subsequently, it forwards this updated manifest to the [Beehive](#beehive). For more information, view the documentation [here](https://github.com/waggle-sensor/wes-chirpstack-device-tracker).

### Lorawan Listener Plugin
The LoRaWAN Listener is a plugin designed to publish measurements collected from LoRaWAN devices. It simplifies the process of extracting and publishing valuable data from these devices. For more information about the plugin view the plugin page [here](https://portal.sagecontinuum.org/apps/app/flozano/lorawan-listener).

### Lorawan Device Profile Templates

[Device Profile Templates](https://www.chirpstack.io/docs/chirpstack/use/device-profile-templates.html#device-profile-templates) simplify the process of onboarding devices to a Node's ChirpStack server. You can create a device template directly through the Node's ChirpStack server UI or by contributing to our [Device Repository](https://github.com/waggle-sensor/wes-lorawan-device-templates?tab=readme-ov-file#waggle-device-repository-for-lorawan).

The Device Repository is a key resource that contains information about various LoRaWAN end devices, making it easier to catalog and onboard these devices to our Nodes' ChirpStack servers. We encourage you to contribute details about your devices to help other Sage users efficiently connect their devices. Once your device is added to our repository, it becomes available across all Nodes, streamlining the workflow for anyone who wants to connect a similar Lorawan device to a Node.

>NOTE: Node's sync with our Device Repository every hour.

If you prefer to keep your device configuration private, you can still add it directly to a Node's ChirpStack server using the UI. In this case, the configuration will remain exclusive to that particular Node.

> For more information and tutorials on how to add a device, visit: [wes-lorawan-device-templates](https://github.com/waggle-sensor/wes-lorawan-device-templates?tab=readme-ov-file#waggle-device-repository-for-lorawan)

### Lorawan Device Compatibility

The Wild Sage Node is designed to support a wide range of Lorawan devices, ensuring flexibility and adaptability for various applications. If you are wondering which Lorawan devices can be connected to a Wild Sage Node, the device must have the following tech specs:

- designed for US915 (902–928 MHz) frequency region.
- compatible with Lorawan Mac versions 1.0.0 - 1.1.0
- compatible with Chirpstack's Lorawan Network Server
- The device supports Over-The-Air Activation (OTAA) or Activation By Personalization (ABP)
- The device has a Lorawan device class of A, B, or C

It is important to note that our Wild Sage Nodes use US915 sub band 2(903.9-905.3 MHz). If you wish to learn more about our Lorawan Gateway, please visit our [portal](https://portal.sagecontinuum.org/sensors/). For inquiries about supporting Lorawan regions other than US915, please [Contact Us](../contact-us.md).

#### Device Examples

Whether you are designing your own Lorawan sensor, looking for a Lorawan data logger, or seeking an off-the-shelf Lorawan device the Wild Sage Node will support it, we have examples for you:

- **Designing your own Lorawan sensor?**
  - [Arduino MKR WAN 1310](https://docs.arduino.cc/hardware/mkr-wan-1310/)

- **Looking for a Lorawan data logger?**
  - [ICT International MFR Node](https://ictinternational.com/product/mfr-node/)

- **Looking for an off-the-shelf Lorawan device?**
  - [ICT International SFM1X Sap Flow Meter](https://ictinternational.com/product/sfm1x-sap-flow-meter/)

- **Seeking Lorawan device manufacturers?**
  - [ICT International](https://ictinternational.com/)
  - [RAKwireless](https://www.rakwireless.com/en-us)
  - [The Things Network Device Marketplace](https://www.thethingsnetwork.org/marketplace/products/devices)
  - [DecentLab](https://www.decentlab.com)


# Developer quick reference


## Disclaimer
:warning: This is a quick-reference guide, not a complete guide to making a plugin.
Use this to copy-paste commands while working on plugins and to troubleshoot them in the testing and scheduling stages.
Please consult the official :green_book:[Plugin Tutorials](/docs/tutorials/edge-apps/intro-to-edge-apps) for detailed guidance.


## Tips
:information_source:  Plugin=App

:green_book: = recommended code docs and tutorials from Sage.

:point_right: First make __a minimalistic__ app with a __core functionality__ to test on the node. Later you may add all the options you want.

:point_up: Avoid making a plugin from scratch. Use another plugin or this [template](https://github.com/waggle-sensor/edge-app-template) for your first plugin or use :new: [Cookiecutter Template](https://github.com/waggle-sensor/cookiecutter-sage-app).

:warning: Repository names should be all in small alphanumeric letters and `-` (Do not use `_`)




Requirements
: Install Docker, git, and Python

## Components of a plugin
Typical components of a Sage plugin are described below:
### 1. An application
This is just your usual Python program, either a single .py script or a set of directories with many components (e.g. ML models, unit tests, test data, etc).

:point_right: First do this step on your machine and perfect it until you are happy with the core functionality.

`app/app.py*`
: the main Python file (sometimes also named **`main.py`**) contains the code that defines the functionality of the plugin or calls other scripts to do tasks. It usually has `from waggle.plugin import Plugin` call to get the data from in-built sensors and publishes the output.

Note: Variable names in `plugin.publish` should be descriptive and specific.

> Install [pywaggle](https://github.com/waggle-sensor/pywaggle) `pip3 install -U 'pywaggle[all]'`


`app/test.py`
: optional but recommended file, contains the unit tests for the plugin.

### 2. Dockerizing the app

:point_right: Put everything in a Docker container using a waggle base image and make it work. This may require some work if libraries are not compatible. Always use the latest base images from [Dockerhub](https://hub.docker.com/r/waggle/plugin-base/tags)

`Dockerfile*`
: contains instructions for building a Docker image for the plugin. It specifies the waggle base image from [dockerhub](https://hub.docker.com/r/waggle/plugin-base/tags), sets up the environment, installs dependencies, and sets the __entrypoint__ for the container.

:warning: Keep it simple `ENTRYPOINT ["python3", "/app/app.py"]`

`requirements.txt*`
: lists the Python dependencies for the plugin. It is used by the Dockerfile to install the required packages using `pip`.

`build.sh`
: is an optional shell script to automate building the complicated Docker image with tags etc.

`Makefile`
: optional but the recommended file includes commands for building the Docker image, running tests, and deploying the plugin.

### 3. ECR configs and docs
You can do this step (_except **sage.yaml**_) after testing on the node but before the [ECR submission](#edge-code-repository). :smile:

`sage.yaml*`
: is the configuration file useful for ECR and job submission? Most importantly it specifies the version and input arguments.

`README.md` and `ecr-meta/ecr-science-description.md*`
: a Markdown file describing the scientific rationale of the plugin as an extended abstract. This includes a description of the plugin, installation instructions, usage examples, data downloading code snippets, and other relevant information.

:bulb: Keep the same text in both files and follow the template of **ecr-science-description.md**.

`ecr-meta/ecr-icon.jpg`
: is an icon (512px x 512px or smaller) for the plugin in the Sage portal.


`ecr-meta/ecr-science-image.jpg`
: is a key image or figure plot that best represents the scientific output of the plugin.

:::info
:green_book: Check Sage Tuorial [Part1](/docs/tutorials/edge-apps/intro-to-edge-apps) and [Part2](/docs/tutorials/edge-apps/creating-an-edge-app)
:::

## Getting access to the node

1. Follow this page: https://portal.sagecontinuum.org/account/access to access the nodes.
2. To test your connection the first time, execute `ssh waggle-dev-sshd` and enter _your ssh key passphrase_. You should get the following output,

> Enter passphrase for key **/Users/bhupendra/.ssh/id_rsa**:
> no command provided
> Connection to 192.5.86.5 closed.
>
> Enter the passphrase to continue.


3. To connect to the node, execute `ssh waggle-dev-node-V032` and enter your _passphrase_ (required twice).

You should see the following message,
> We are connecting you to node V032

:::info
:green_book: See [Sage Tuorial: Part 3](/docs/tutorials/edge-apps/testing-an-edge-app) for details on this topic.
:::


## Testing plugins on the nodes

:::danger
:warning: Do not run any app or install packages directly on the node. Use Docker container or `pluginctl` commands.
:::

### 1. Download and run it

#### Download
- If you have not already done it, you need your plugin in a public GitHub repository at this stage.
- To test the app on a node, go to nodes W0xx (e.g. W023) and clone your repo there using the command `git clone`.
- At this stage, you can play with your plugin in the docker container until you are happy. Then if there are changes made to the plugin, I reccomend replicating the same in your local repository and pushing it to the github and node.
- or do `git commit -am 'changes from node'` and `git push -u origin main`.
- However, before commiting from node, you must run following commands at least once in your git repository on the node.
`git config [--locale] user.name "Full Name"`
`git config [--locale] user.email "email@address.com"`

:::danger
:warning: Make sure your **Dockerfile** has a proper **entrypoint** or the `pluginctl` run will fail.
:::

#### Testing with Pluginctl

:::info
:green_book: For more details on this topic check [pluginctl docs](https://github.com/waggle-sensor/edge-scheduler/tree/main/docs/pluginctl).
:::

1. Then to test execute the command `sudo pluginctl build .`. This will output the plugin-image registry address at the end of the build. Example: `10.31.81.1:5000/local/my-plugin-name`
4. To run the plugin without input argument, use `sudo pluginctl deploy -n <some-unique-name> <10.31.81.1:5000/local/my-plugin-name>`
5.  Execute the command with input arguments. `sudo pluginctl deploy -n <some-unique-name> <10.31.81.1:5000/local/my-plugin-name> -- -i top_camera`.
7.  If you need GPU, use the selector `sudo pluginctl deploy -n <some-unique-name> <10.31.81.1:5000/local/my-plugin-name> -- -i top_camera`.
8. :exclamation: `--` is a separator. After the `--` all arguments are for your entrypoint i.e. app.py.
9. To check running plugins, execute `sudo pluginctl ps`.
10. To stop the plugin, execute `sudo pluginctl rm cloud-motion`.
11. To check the log `pluginctl logs cloud-motion`
:warning:Do not forget to stop the plugins after testing or it will run forever.

### Testing USBSerial devices
:point_right:The USBserial device template is in [Cookiecutter Template](https://github.com/waggle-sensor/cookiecutter-sage-app). Also check [wxt536](https://github.com/jrobrien91/waggle-wxt536) plugin.

Steps for working with a USB serial device

1. First, you need to confirm which computing unit the USB device is connected to, RPi or nxcore.
2. Then, you add the `--selector` and `--privileged` options to the `pluginctl`  command during testing and specifying the same in the **job.yaml** for scheduling.
3. To test the plugin on _nxcore_, which has the USB device, use the command `sudo pluginctl run -n testname --selector zone=core --privileged 10.31.81.1:5000/local/plugin-name`.
4. The `--selector` and `--privileged` attributes should be added to the _pluginSpec_ in the job submission script as shown in the example YAML code.
5. You can check which computing unit is being used by the edge scheduler by running the `kubectl describe pod` command and checking the output.



:warning: Re/Check that you are using the correct USB port for the device if getting empty output or _folder not found_ error.


### 2. Check if it worked?
Login to the Sage portal and follow the instructions from the section [See Your Data on Sage Portal](https://hackmd.io/iKUbbfZ7RYGbXT_tnBd1vg?both#See-Your-Data-on-Sage-Portal)

### 3. Check why it failed?
When you encounter a failing/long pending job with an error, you can use the following steps to help you diagnose the issue:

1. First check the Dockerfile **entrypoint**.
2. Use the command `sudo kubectl get pod` to get the name of the pod associated with the failing job.
3. Use the command `sudo kubectl logs <<POD_NAME>>` to display the logs for the pod associated with the failing job. These logs will provide you with information on why the job failed.
4. Use the command `sudo kubectl describe pod POD_NAME` to display detailed information about the pod associated with the failing job.
5. This information can help you identify any issues with the pod itself, such as issues with its configuration or resources.

By following these steps, you can better understand why the job is failing and take steps to resolve the issue.


### 4. Troubleshooting inside the container using pluginctl
Follow this [tutorial](https://github.com/waggle-sensor/edge-scheduler/blob/main/docs/pluginctl/tutorial_getintoplugin.md) to get in an already running container to troubleshoot the issue.
If the plugin fails instantly and your are not able to get inside the container use following commands to override the entrypoint

1. First Deploy with Custom Entrypoint `--entrypoint /bin/bash `:
```
sudo pluginctl deploy -n testnc --entrypoint /bin/bash 10.31.81.1:5000/local/plugin-mobotix-scan -- -c 'while true; do date; sleep 1; done'
```
Note the `-c 'while true; do date; sleep 1; done'` instead of your usual plugin arguments.
Now if you do `sudo pluginctl logs testnc` you will see the logs i.e. date.

2. Access the Plugin Container:
```sudo pluginctl exec -ti testnc -- /bin/bash```



## Edge Code Repository
### How to get your plugin on ECR

To publish your Plugin on ECR, follow these steps:
1. Go to https://portal.sagecontinuum.org/apps/.
2. Click on "Explore the Apps Portal".
3. Click on "My Apps". You must be logged in to continue.
4. Click "Create App" and enter your Github Repo URL.
5. 'Click "Register and Build App".
6. On Your app page click on the "Tags" tab to get the registry link when you need to run the job on the node either using `pluginctl` or job script. This will look like:`docker pull registry.sagecontinuum.org/bhupendraraut/mobotix-move:1.23.3.2`
7. Repeat the above process for updating the plugin.

:::warning
After the build process is complete, you need to **make the plugin public** to schedule it.
:::


:point_right: If you have skipped step <a href="#3-ecr-configs-and-docs">3. ECR Configs and Docs</a>, do it before submitting it to the ECR. Ensure that your **`ecr-meta/ecr-science-description.md`** and **`sage.yaml`** files are properly configured for this process.

#### Versioning your code
:::danger
You can not resubmit the plugin to ECR with the same version number again.
:::
- So think about how you change it every time you resubmit to ECR and make your style of versioning. :thinking_face:
- I use _'vx.y.m.d'_ e.g. _'v0.23.3.4'_ but then I can only have 1 version a day, so now I am thinking of adding an incremental integer to it.

### After ECR registry test (generally not required)
1. Generally successfully tested plugins just work. However, in case they are failing in the scheduled jobs after running for a while or after successfully running in the above tests, do the following.
2. To test a plugin on a node after it has been built on the ECR, follow these steps:
`
sudo pluginctl run --name test-run registry.sagecontinuum.org/bhupendraraut/cloud-motion:1.23.01.24 -- -input top
`
2. This command will execute the plugin with the specified ECR image (version 1.23.01.24), passing the "-input top" argument to the plugin (Note `--` after the image telling `pluginctl` that these arguments are for the plugin).

:point_right: Note the use of `sudo` in all `pluginctl` and  `docker` commands on the node.

Assuming that the plugin has been installed correctly and the ECR image is available, running this command should test the "test-motion" plugin on the node.

You may also have to call the `kubectl <POD>` commands as in the testing section if this fails.

## Scheduling the job
:::warning
:exclamation: If you get an error like `registry does not exist in ECR`, then check that your plugin is made public.
:::


- Follow this [link](/docs/tutorials/schedule-jobs) to get an understanding of how to submit a job
- Here are the parameters we set for the Mobotix sampler plugin,

```less=
-name thermalimaging registry.sagecontinuum.org/bhupendraraut/mobotix-sampler:1.22.4.13 \
   --ip 10.31.81.14 \
   -u userid \
   -p password \
   --frames 1 \
   --timeout 5 \
   --loopsleep 60
```
- Your science rule can be a cronjob (More information can be found [here](https://github.com/waggle-sensor/sciencerule-checker/blob/master/docs/supported_functions.md#cronjobprogram_name-cronjob_time)
- This runs every 15 minutes
`"thermalimaging": cronjob("thermalimaging", "*/15 * * * *")`.
- Use [Crontab Guru](https://crontab.guru/).
- You can also make it triggered by a value. Please [read this](https://github.com/waggle-sensor/sciencerule-checker/blob/master/docs/supported_functions.md) for supported functions.


### Scheduling scripts
:sparkles: Check user friendly [job submission UI](https://portal.sagecontinuum.org/jobs/all-jobs).

:green_book: Check [sesctl docs](https://github.com/waggle-sensor/edge-scheduler/tree/main/docs/sesctl) for command line tool.


1. :point_up: Do not use `_`, upper case letters or `.` in the job name. Use only lowercase letters, numbers and `-`.
2. :point_up: Ensure that the plugin is set to 'public' in the Sage app portal.


### `job.yaml` example for USB device
```yaml=
name: atmoswxt
plugins:
- name: waggle-wxt536
  pluginSpec:
    image: registry.sagecontinuum.org/jrobrien/waggle-wxt536:0.23.4.13
    privileged: true
    selector:
      zone: core
nodeTags: []
nodes:
  W057: true
  W039: true
scienceRules:
- 'schedule("waggle-wxt536"): cronjob("waggle-wxt536", "1/10 * * * *")'
successCriteria:
- WallClock('1day')
```

### Multiple jobs example
If you want to run your plugins not all at the same time. Use this example.

```yaml=
name: w030-k3s-upgrade-test
plugins:
- name: object-counter-bottom
  pluginSpec:
    image: registry.sagecontinuum.org/yonghokim/object-counter:0.5.1
    args:
    - -stream
    - bottom_camera
    - -all-objects
    selector:
      resource.gpu: "true"
- name: cloud-cover-bottom
  pluginSpec:
    image: registry.sagecontinuum.org/seonghapark/cloud-cover:0.1.3
    args:
    - -stream
    - bottom_camera
    selector:
      resource.gpu: "true"
- name: surfacewater-classifier
  pluginSpec:
    image: registry.sagecontinuum.org/seonghapark/surface_water_classifier:0.0.1
    args:
    - -stream
    - bottom_camera
    - -model
    - /app/model.pth
- name: avian-diversity-monitoring
  pluginSpec:
    image: registry.sagecontinuum.org/dariodematties/avian-diversity-monitoring:0.2.5
    args:
    - --num_rec
    - "1"
    - --silence_int
    - "1"
    - --sound_int
    - "20"
- name: cloud-motion-v1
  pluginSpec:
    image: registry.sagecontinuum.org/bhupendraraut/cloud-motion:1.23.02.20
    args:
    - --input
    - bottom_camera
- name: imagesampler-bottom
  pluginSpec:
    image: registry.sagecontinuum.org/theone/imagesampler:0.3.1
    args:
    - -stream
    - bottom_camera
- name: audio-sampler
  pluginSpec:
    image: registry.sagecontinuum.org/seanshahkarami/audio-sampler:0.4.1
nodeTags: []
nodes:
  W030: true
scienceRules:
- 'schedule(object-counter-bottom): cronjob("object-counter-bottom", "*/5 * * * *")'
- 'schedule(cloud-cover-bottom): cronjob("cloud-cover-bottom", "01-59/5 * * * *")'
- 'schedule(surfacewater-classifier): cronjob("surfacewater-classifier", "02-59/5
  * * * *")'
- 'schedule("avian-diversity-monitoring"): cronjob("avian-diversity-monitoring", "*
  * * * *")'
- 'schedule("cloud-motion-v1"): cronjob("cloud-motion-v1", "03-59/5 * * * *")'
- 'schedule(imagesampler-bottom): cronjob("imagesampler-bottom", "04-59/5 * * * *")'
- 'schedule(audio-sampler): cronjob("audio-sampler", "*/5 * * * *")'
successCriteria:
- Walltime(1day)

```

here
objecct-counter runs at 0, 5, 10, etc
cloud-cover: 1, 6, 11, etc.
surface water: 2, 7, 12, etc.
cloud-motion: 3, 8, 13, etc.
image-sampl: 4, 9, 14, etc.


### Debugging failed jobs
Do you know how to identify why a job is failing

1. :sparkles: When the job failures are seen as `red` markers on your [job page](https://portal.sagecontinuum.org/jobs/my-jobs), you can click them to see the error.
![click on red markers](https://i.imgur.com/xPXERPX.png)

![](https://i.imgur.com/GmStINF.png)


2. Or detail errors can be found using using `sage_data_client`
- Requirements: `sage_data_client` and [utils.py](https://github.com/waggle-sensor/edge-scheduler/blob/main/scripts/analysis/utils.py)
- By specifying the plugin name and node, the following code will print out the reasons for job failure within the last 60 minutes.


```python=
from utils import *

mynode = "w030"

myplugin = "water"
df = fill_completion_failure(parse_events(get_data(mynode, start="-60m")))
for _, p in df[df["plugin_name"].str.contains(myplugin)].iterrows():
    print(p["error_log"])
```



## Downloading the data

[Sage docs for accessing-data](/docs/tutorials/accessing-data)


### See Your Data on Sage Portal
To check your data on Sage Portal, follow these steps:
1. Click on the Data tab at the top of the portal page.
2. Select Data Query Browser from the dropdown menu.
3. Then, select your app in the filter.
This will show all the data that is uploaded by your app using the `plugin.publish()` and `plugin.upload()` methods.

In addition, you can data visualize as a time series and select multiple variables to visualize together in a chart, which can be useful for identifying trends or patterns.

![](https://i.imgur.com/5W9jAfw.png)


### Download all images with wget
1. Visit https://training-data.sagecontinuum.org/
2. select the node and period for data.
3. Select the required data and download the text file _urls-xxxxxxx.txt_ with urls
4. To select only the top camera images, use the `vim` command: `g/^\(.*top\)\@!.*$/d`. This will delete URLs that do not contain the word 'top'
5. Copy the following command from the website and run it in your terminal. `wget -r -N -i urls-xxxxxxx.txt`


### Sage data client for text data
- Sage data client [python Notebook Example](https://github.com/sagecontinuum/sage-data-client/blob/main/examples/plotting_example.ipynb)
- pypi [link](https://pypi.org/project/sage-data-client/)
`pip install sage-data-client`

:::info
:green_book: Documentation for [accessing the data.](https://docs.sagecontinuum.org/docs/tutorials/accessing-data)
:::




### Querying data example

The `sage_data_client` provides `query()` function which takes the parameters:

```python
import sage_data_client
import pandas as pd

df = sage_data_client.query(
    start="2023-01-08T00:00:09Z",  # Start time in "YYYY-MM-DDTHH:MM:SSZ" or "YYYYMMDD-HH:MM:SS" format
    end="2024-01-08T23:23:24Z",    # End time in the same format as start time
    filter={
        "plugin": ".*mobotix-scan.*",  # Regex for filtering by plugin name
        "vsn": "W056",                # Specific node identifier
        "name": "upload",             # Specific data field
        "filename": ".*_position1.nc" # Regex for filtering filenames
    }
)

df.sort_values('timestamp')
df
```

### Filter Criteria
- `start` and `end`: Time should be specified in UTC, using the format `YYYY-MM-DDTHH:MM:SSZ` or `YYYYMMDD-HH:MM:SS`.
- `filter`: A dictionary for additional filtering criteria. Each key is a column name in the `df`.
- Use regular expressions (denoted as `.*pattern.*`) for flexible matching within text fields like `plugin` or `filename`.


### Downloading Files
Use additional pandas operations on `df` to to include only the records of interest and download the files using a function like the one provided below, which gets the URLs in the `value` column, using authentication.

```python
import requests
import os
from requests.auth import HTTPBasicAuth

uname = 'username'
upass = 'token_as_password'

def download_files(df, download_path, uname, upass):
   # check download directory
   if not os.path.exists(download_path):
      os.makedirs(download_path)

   for index, row in df.iterrows():
      # 'value' column has url
      url = row['value']

      filename = url.split('/')[-1]

      # Download using credentials
      response = requests.get(url, auth=HTTPBasicAuth(uname, upass))
      if response.status_code == 200:
         # make the downloads path
         file_path = os.path.join(download_path, filename)
         # Write a new file
         with open(file_path, 'wb') as file:
         file.write(response.content)
         print(f"Downloaded {filename} to {file_path}")
      else:
         print(f"Failed to download {url}, status code: {response.status_code}")

# usage
download_files(df, '/Users/bhupendra/projects/epcape_pier/data/downloaded/nc_pos1', uname, upass)
```

### More data analysis resources
- [Sage Examples](https://github.com/sagecontinuum/sage-data-client/tree/main/examples)
- [CROCUS Cookbooks](https://crocus-urban.github.io/instrument-cookbooks/README.html)


## Miscellaneous
### Find PT Mobotix thermal camera ip on the node
Login to the node where the PTmobotix camera is connected.
1. run `nmap -sP 10.31.81.1/24`

```
Nmap scan report for ws-nxcore-000048B02D3AF49F (10.31.81.1)
Host is up (0.0012s latency).
Nmap scan report for switch (10.31.81.2)
Host is up (0.0058s latency).
Nmap scan report for ws-rpi (10.31.81.4)
Host is up (0.00081s latency).
Nmap scan report for 10.31.81.10
Host is up (0.0010s latency).
Nmap scan report for 10.31.81.15
Host is up (0.00092s latency).
Nmap scan report for 10.31.81.17
Host is up (0.0014s latency).
Nmap done: 256 IP addresses (6 hosts up) scanned in 2.42 seconds
```

2. From the output run any command for each ip
e.g.
`curl -u admin:meinsm  -X POST  http://10.31.81.15/control/rcontrol?action=putrs232&rs232outtext=%FF%01%00%0F%00%00%10`

3. The ip for which output is `OK` is the Mobotix.

### SSH 'Broken Pipe' Issue and Solution
A 'Broken pipe' occurs when the SSH session to waggle-dev-node is inactive for longer than 10/15 minutes, resulting in a closed connection.

```
client_loop: send disconnect: Broken pipe
Connection to waggle-dev-node-w021 closed by remote host.
Connection to waggle-dev-node-w021 closed.
```


##### Solution
To prevent the SSH session from timing out and to maintain the connection, the following configuration options can be added to the SSH config file:
```ssh
# Keep the SSH connection alive by sending a message to the server every 60 seconds
Host *
  TCPKeepAlive yes
  ServerAliveInterval 60
  ServerAliveCountMax 999
```

---
sidebar_label: pluginctl
sidebar_position: 1
---

# pluginctl: a tool to develop and test plugins on a node
We developed the tool `pluginctl` to help end users develop and test their edge application (i.e., plugin) on a node before registering the plugin in [Edge code repository](../about/architecture.md#edge-code-repository-ecr). The tool helps on simplifying the process of testing the edge code and making changes as needed for development, by buildig the code into a container, running the container inside the node, and checking the result from the container.

All of Waggle nodes have the tool already installed. For plugin developers who have access to nodes, they can simply type the following to start with once they are logged into a node,
```bash
sudo pluginctl
```

The in-depth tutorials on the functionalities that `pluginctl` offers can be found in the [README](https://github.com/waggle-sensor/edge-scheduler/tree/main/docs/pluginctl#readme).

---
sidebar_label: sesctl
sidebar_position: 2
---

# sesctl: a tool to schedule jobs in Waggle edge computing
The tool `sesctl` is a command-line tool that communicates with an [Edge scheduler](../about/architecture.md#edge-scheduler-es) in the cloud to manage user jobs. Users can create, edit, submit, suspend, and remove jobs via the tool.

## Installation
The tool can be downloaded from the [edge scheduler repository](https://github.com/waggle-sensor/edge-scheduler/releases) and be run on person's desktop or laptop.

:::note
Please make sure to download the correct version of the tool based on the system architecture. For example, if you run it on a Mac download `sesctl-darwin-amd64`.
:::


```bash
chmod +x sesctl-<system>-<arch>
ln sesctl-<system>-<arch> sesctl
sesctl
```

## Submit a job
You can follow the [tutorial](../tutorials/schedule-jobs.md) to submit an example job to understand how to design your own job.

## For more tutorials
The in-depth tutorials on the functionalities that `sesctl` offers can be found in the [README](https://github.com/waggle-sensor/edge-scheduler/tree/main/docs/sesctl#readme).

---
sidebar_label: Trigger examples
sidebar_position: 3
---

# Trigger Examples

This page provides a few examples of triggers within Sage. Triggers are programs which generally use data and events from the edge or cloud to automatically drive or notify other behavior in the system.

## Cloud-to-Edge Examples

Cloud-to-edge triggers are programs running in the cloud which monitor events or external data sources and then, in response, change some behavior on the nodes.

### [Severe Weather Trigger](https://github.com/waggle-sensor/severe-weather-trigger-example)

This example starts and stops jobs in response to severe weather events scraped from the National Weather Service API.

### [Wildfire Trigger](https://github.com/waggle-sensor/wildfire-trigger-example)

This example looks at results from the smoke detector job and modify its own scheduling interval in response. The concept is that as smoke is detected, we want to run more frequent detections.

## Edge-to-Cloud Examples

Edge-to-cloud triggers are programs which monitor data published from the nodes and use it, potentially along with additional data sources, to perform some computation or actions.

### [Sage Data Client Batch Trigger](https://github.com/sagecontinuum/sage-data-client/blob/main/examples/trigger-batch.py)

This is a simple batch trigger example of using [Sage Data Client](https://pypi.org/project/sage-data-client/) to print nodes where the internal mean temperature exceeds a threshold every 5 minutes.

### [Sage Data Client Stream Trigger](https://github.com/sagecontinuum/sage-data-client/blob/main/examples/trigger-stream.py)

This is an example of using [Sage Data Client](https://pypi.org/project/sage-data-client/) to watch the data stream and print nodes where the internal temperature exceeds a threshold.

---
sidebar_position: 5
---

# Access Waggle sensors
A Waggle sensor is an entity that produces measurements of a phenomenon and that helps users analyze what is happening in the environment. There are sensors already hosted by Waggle and also sensors that are being integrated into Waggle as a user-hosted sensor. A sensor does not necessarily mean a physical device, but can be a program producing measurements from data -- we call it __software-defined sensor__. Once those sensors become available in Waggle nodes edge applications running inside the nodes can pull measurements from the sensors to process them.

In general, Waggle sensors are desinged to be accessible from any edge applications running on the Waggle node that hosts the sensors, but can be limited their access to groups and personnel. For example, a pan-tilt-zoom featured camera may be only accessed from authorized applications in order to prevent other applications from operating the camera. Ideally, Waggle sensors can form and support the Waggle ecosystem where sensor measurements are integrated and used by edge applications for higher level computation and complex decision making.

## Waggle physical sensors
![Figure 1: Sensors of Waggle node](./images/waggle_node.jpg)
The Waggle node is designed to accommodate sensors commonly used to support environmental science, but not limited to host other sensors. The currently supported sensors are,

_NOTE: not all Waggle nodes have the same set of sensors, and the sensor configuration depends on what to capture from the environment where the node is deployed_

<table className="full-width">
  <tbody>
    <tr>
      <td><a href="https://portal.sagecontinuum.org/sensors/BME680">BME680</a></td>
      <td>temperature, humidity, pressure, and gas</td>
      <td>
        <a href="https://portal.sagecontinuum.org/query-browser?type=names&names=env.temperature">preview</a>
      </td>
    </tr>
    <tr>
      <td><a href="https://portal.sagecontinuum.org/sensors/RG-15">RG-15</a></td>
      <td>rainfall</td>
      <td><a href="https://portal.sagecontinuum.org/query-browser?apps=.*plugin-raingauge.*&window=h">preview</a></td>
    </tr>
    <tr>
      <td><a href="https://portal.sagecontinuum.org/sensors/ML1-WS%20IP54">ETS ML1-WS</a></td>
      <td>20-16 kHz microphone recording sound</td>
      <td rowSpan="5"></td>
    </tr>
    <tr>
      <td><a href="https://portal.sagecontinuum.org/sensors/XNV-8080R">XNV-8080R</a></td>
      <td>5 MP camera with 92.1 degree horizontal and 67.2 degree vertical angle view</td>
    </tr>
      <tr>
      <td><a href="https://portal.sagecontinuum.org/sensors/XNV-8082R">XNV-8082R</a></td>
      <td>6 MP camera with 114 degree horizontal and 62 degree vertical angle view</td>
    </tr>
      <tr>
      <td><a href="https://portal.sagecontinuum.org/sensors/XNF-8010RV">XNF-8010RV</a></td>
      <td>6 MP fisheye camera with 192 degree horizontal and vertical angle view</td>
    </tr>
    <tr>
      <td><a href="https://portal.sagecontinuum.org/sensors/XNV-8081Z">XNV-8081Z</a></td>
      <td>5 MP digital pan-tilt-rotate-zoom camera</td>
    </tr>
  </tbody>
</table>

Any collaborators and user communities can bring up their sensors to Waggle node. The node can easily host sensor devices that support serial interface as well as network interface (e.g., http, rtsp, etc). Other currently supported user sensors include:

- Software-defined Radio: detecting raindrops and snow flakes
- Radiation detector: radiation detector
- LIDAR: distance of nearby objects
- Mobotix: infrared camera

[[view more...](https://portal.sagecontinuum.org/sensors)]

## Waggle software-defined sensors
Software-defined sensors are limitless as edge applications define them. You can start building your edge application that publishes outputs using [PyWaggle's basic example](https://github.com/waggle-sensor/pywaggle/blob/main/docs/writing-a-plugin.md#basic-example) that can become a software-defined sensor. Later, such outputs can be consumed by other edge applications to produce higher level information about the measurements. A few example of Waggle software-defined sensors are,

- [Object Counter](https://portal.sagecontinuum.org/apps/app/yonghokim/object-counter): `env.count.OBJECT` counts objects from an image, where `OBJECT` is the object name that is recognized
- [Cloud Coverage Estimator](https://portal.sagecontinuum.org/apps/app/seonghapark/cloud-cover): `env.coverage.cloud` provides a percentage of cloud covered in an image

## Access to Waggle sensors
![Figure 2: Access to Waggle sensors](./images/access_to_sensors.svg)

Waggle sensors are integrated into Waggle using the PyWaggle library. PyWaggle utilizes AMQP, [the message publishing and subscribing mechanism](https://www.amqp.org), to support exchanging sensor measurements between device plugins and edge applications. An edge application can subscribe and process those measurements using [PyWaggle's subscriber](https://github.com/waggle-sensor/pywaggle/blob/main/docs/writing-a-plugin.md#subscribing-to-other-measurements). The application then produces its output and publishes it as a measurement back to the system using [PyWaggle publisher](https://github.com/waggle-sensor/pywaggle/blob/main/docs/writing-a-plugin.md#more-about-the-publish-function).

PyWaggle often provides edge applications direct access to physical sensors. For sensors that support realtime protocols like RTSP and RTP and others, PyWaggle exposes those protocols to edge applications, and it is up to the applications to process data using given protocol. For example, RTSP protocol can be handled by OpenCV's VideoCapture class inside an application. If any physical sensor device that requires a special interfacing to the device, an edge application that supports the interfacing need to run in order to publish sensor measurements to the system, and later those measurements are used by other edge applications.

## Example: sampling images from camera
It is often important to sample images from cameras in the field to create initial dataset for a machine learning algorithm. [The example](https://github.com/waggle-sensor/pywaggle/blob/main/docs/writing-a-plugin.md#accessing-a-video-stream) describes how to access to a video stream from a camera sensor using PyWaggle.

## Bring your own sensor to Waggle
Users may need to develop their own device plugin to expose the sensor to the system, or to publish measurement data from the sensor to the cloud. Unlike an edge application or software-defined sensors, device plugins communicating with a physical sensor may need special access, e.g. serial port, in order to talk to the sensor attached to Waggle node. Such device plugin may need to be verified by the Waggle team. Visit the [Building your own Waggle device](./create-waggle.md) page for the guide to set up your Waggle device.

To integrate your sensor device into Waggle, head over to the [Contact Us](../contact-us.md) page

---
sidebar_position: 4
---

# Access and use data

![Data Movement](./images/data_movement.svg)

Raw sensor data is collected by edge code. This edge code can either talk to sensor hardware directly or may obtain data from an abstraction layer (not show in image above). Edge code may forward unprocessed sensor data, do light processing to convert raw sensor values into final data products, or may use CPU/GPU-intensive workloads (e.g. AI application) to extract information from data-intensive sensors such as cameras, microphone or LIDAR.

Sensor data from nodes that comes in numerical or textual form (e.g. temperature) is stored natively in our time series database. Sensor data in form of large files (images, audio, movies..) is stored in the Waggle object store, but is referenced in the time series data (thus the dashed arrow in the figure above). Thus, the primary way to find all data (sensor and large files) is via the Waggle sensor query API described below.

Currently the Waggle sensor database contains data such as:

- Relative humidity, barometric pressure, ambient temperature and gas (VOC) [BME680](https://www.bosch-sensortec.com/products/environmental-sensors/gas-sensors/bme680/).
- Rainfall measurements [(Hydreon RG-15)](https://sage-commons.sdsc.edu/dataset/rg-15).
- AI-based cloud coverage estimation from camera images.
- AI-based object counts from camera images.
- System data such as uptime, cpu and memory.

Data can be accessed in realtime via our data API or in bulk via data bundles.

## Data API

Waggle provides a **data API** for immediate and flexible access to sensor data via search over time and metadata tags. It is primarily intended to support exploratory and near real time use cases.

Due to the wide variety of possible queries, we do not attempt to provide DOIs for results from the data API. Instead, we leave it up to users to organize and curate datasets for their own applications. Long term, curated data is instead provided via **data bundles**.

There are two recommended approaches to working with the Data API:

1. Using the [Python Sage Data Client](https://pypi.org/project/sage-data-client/).
2. Using the HTTP API.

Each is appropriate for different use cases and integrations, but generally the following rule applies:

_If you just want to get data into a Pandas dataframe for analysis and plotting, use the sage-data-client, otherwise use the HTTP API._

### Using Sage data client

The Sage data client is a Python library which streamlines querying the data API and getting the results into a Pandas dataframe. For details on installation and usage, please see the [Python package](https://pypi.org/project/sage-data-client/).

### Using HTTP API

This example shows how to retrieve data the latest data from a specific sensor (you can adjust the `start` field if you do not get any recent data):

```console
curl -H 'Content-Type: application/json' https://data.sagecontinuum.org/api/v1/query -d '
{
    "start": "-10s",
    "filter": {
        "sensor": "bme680"
    }
}
'

```
Example results:
```json
{"timestamp":"2021-08-09T19:26:03.880781217Z","name":"iio.in_humidityrelative_input","value":70.905,"meta":{"node":"000048b02d15bdcd","plugin":"plugin-metsense:0.1.1","sensor":"bme680"}}
{"timestamp":"2021-08-09T19:26:03.878659392Z","name":"iio.in_pressure_input","value":975.78,"meta":{"node":"000048b02d15bdcd","plugin":"plugin-metsense:0.1.1","sensor":"bme680"}}
{"timestamp":"2021-08-09T19:26:03.872652127Z","name":"iio.in_resistance_input","value":93952,"meta":{"node":"000048b02d15bdcd","plugin":"plugin-metsense:0.1.1","sensor":"bme680"}}
{"timestamp":"2021-08-09T19:26:03.874998057Z","name":"iio.in_temp_input","value":27330,"meta":{"node":"000048b02d15bdcd","plugin":"plugin-metsense:0.1.1","sensor":"bme680"}}
```

:::tip
More details of using the data API and the data model can be found [here](https://github.com/waggle-sensor/waggle-beehive-v2/blob/main/docs/querying-measurements.md#query-api) and [here](https://github.com/waggle-sensor/waggle-beehive-v2/blob/main/docs/querying-measurements.md#data-model).
:::

## Data bundles

**Data bundles** provide sensor data and associated metadata in a single, large, downloadable file.  Soon, each Data Bundle available for download will have a DOI that can be used for publication citations.

Data Bundles are compiled nightly and may be downloaded in [this archive](https://web.lcrc.anl.gov/public/waggle/sagedata/SAGE-Data.tar).

## Accessing file uploads

User applications can upload files for AI training purposes. These files stored in an S3 bucket hosted by the [Open Storage Network](https://www.openstoragenetwork.org/).

To find these files use the filter `"name":"upload"` and specify additional filters to limit search results, for example:

```console
curl -s -H 'Content-Type: application/json' https://data.sagecontinuum.org/api/v1/query -d '{
  "start": "2021-09-10T12:51:36.246454082Z",
  "end":"2021-09-10T13:51:36.246454082Z",
  "filter": {
    "name":"upload",
    "plugin":"imagesampler-left:0.2.3"
    }
  }'
```

Output:
```json
{"timestamp":"2021-09-10T13:19:27.237651354Z","name":"upload","value":"https://storage.sagecontinuum.org/api/v1/data/sage/sage-imagesampler-left-0.2.3/000048b02d05a0a4/1631279967237651354-2021-09-10T13:19:26+0000.jpg","meta":{"job":"sage","node":"000048b02d05a0a4","plugin":"imagesampler-left:0.2.3","task":"imagesampler-left:0.2.3"}}
{"timestamp":"2021-09-10T13:50:32.29028603Z","name":"upload","value":"https://storage.sagecontinuum.org/api/v1/data/sage/sage-imagesampler-left-0.2.3/000048b02d15bc3d/1631281832290286030-2021-09-10T13:50:32+0000.jpg","meta":{"job":"sage","node":"000048b02d15bc3d","plugin":"imagesampler-left:0.2.3","task":"imagesampler-left:0.2.3"}}
{"timestamp":"2021-09-10T12:52:59.782262376Z","name":"upload","value":"https://storage.sagecontinuum.org/api/v1/data/sage/sage-imagesampler-left-0.2.3/000048b02d15bdc2/1631278379782262376-2021-09-10T12:52:59+0000.jpg","meta":{"job":"sage","node":"000048b02d15bdc2","plugin":"imagesampler-left:0.2.3","task":"imagesampler-left:0.2.3"}}
{"timestamp":"2021-09-10T13:49:49.084350086Z","name":"upload","value":"https://storage.sagecontinuum.org/api/v1/data/sage/sage-imagesampler-left-0.2.3/000048b02d15bdd2/1631281789084350086-2021-09-10T13:49:48+0000.jpg","meta":{"job":"sage","node":"000048b02d15bdd2","plugin":"imagesampler-left:0.2.3","task":"imagesampler-left:0.2.3"}}
```

For a quick way to only extract the urls from the json objects above, a tool like [jq](https://stedolan.github.io/jq/) can be used:

```console
curl -s -H 'Content-Type: application/json' https://data.sagecontinuum.org/api/v1/query -d '{
  "start": "2021-09-10T12:51:36.246454082Z",
  "end":"2021-09-10T13:51:36.246454082Z",
  "filter": {
    "name":"upload",
    "plugin":"imagesampler-left:0.2.3"
    }
  }' | jq -r .value > urls.txt
```

The resulting file `urls.txt` will look like this:
```text
https://storage.sagecontinuum.org/api/v1/data/sage/sage-imagesampler-left-0.2.3/000048b02d05a0a4/1631279967237651354-2021-09-10T13:19:26+0000.jpg
https://storage.sagecontinuum.org/api/v1/data/sage/sage-imagesampler-left-0.2.3/000048b02d15bc3d/1631281832290286030-2021-09-10T13:50:32+0000.jpg
https://storage.sagecontinuum.org/api/v1/data/sage/sage-imagesampler-left-0.2.3/000048b02d15bdc2/1631278379782262376-2021-09-10T12:52:59+0000.jpg
https://storage.sagecontinuum.org/api/v1/data/sage/sage-imagesampler-left-0.2.3/000048b02d15bdd2/1631281789084350086-2021-09-10T13:49:48+0000.jpg
```

To download the files:
```console
wget -i urls.txt
```

If many files are downloaded, it is better to preserve the directory tree structure to prevent filename collision:
```console
wget -r -i urls.txt
```

### Protected data

While most Waggle data is open and public - some types of data, such as raw images and audio from sensitive locations, may require additional steps:

* You will need a Sage account.
* You will need to sign our Data Use Agreement for access.
* You will need to provide authentication to tools you are using to download files. (ex. wget, curl)

Attempting to download protected files without meeting these criteria will yield a 401 Unauthorized response.

If you've identified protected data you are interested in, please [contact us](/docs/contact-us) so we can help get you access.

In the case of protected files, you'll need to provide authentication to your tool of choice. These will be your portal username and access token which can be found in the [Access Credentials](https://portal.sagecontinuum.org/account/access) section of the site.

![Access Credentials](./images/access-token.png)

These can be provided to tools like wget and curl as follows:

```console
# example using wget
wget --user=<portal-username> --password=<portal-access-token> -r -i urls.txt

# example using curl
curl -u <portal-username>:<portal-access-token> url
```

---
sidebar_position: 6
---

# Cloud compute & HPC on edge data

Waggle provides a number of interfaces which other computing and HPC systems can build on top of. In this section, we explore some of the most common applications of Waggle.

## Triggering on data from the edge

A common application is monitoring data from the edge and triggering actions when values exceed a threshold or an unusual event is detected.

As a getting started example, we demonstrate an outline of how this can be done in Waggle using the [Sage data client](https://github.com/sagecontinuum/sage-data-client).

```python
import sage_data_client
import time

while True:
    # query pressure data in recent 10 minute window
    df = sage_data_client.query(
        start="-10m",
        filter={
            "name": "env.pressure",
            "sensor": "bme680",
        }
    )

    # compute stddev for nodes' pressure data in window
    std = df.groupby("meta.vsn").value.std()

    # find all pressure events exceeding an example threshold
    events = std[std > 8.0]

    # "post" vsn to alert system
    for vsn in events.index:
        print(f"post {vsn} to alert system")

    time.sleep(60)
```

The above code queries a 10 minute window of atmospheric pressure data every minute and "posts" alerts for nodes exceeding a predefined standard deviation threshold.

This example and more can be found in the Sage data client [examples](https://github.com/sagecontinuum/sage-data-client/blob/main/examples/) directory.

---
sidebar_label: Create an account
sidebar_position: 1
---

# Overview

While some Sage features are open for public use, you'll need an approved account to perform tasks such as:

* Accessing protected data.
* Publishing apps to the ECR.
* Scheduling apps on nodes.

In this document, we'll walk though creating an account.

# Creating an account

1. Click on the __Portal__ button in the upper right corner.
2. Click on the __Sign In__ button in the upper right corner.
3. This will take you to the __Globus login page__ where you'll need to provide your organization credentials. If you do not see your organization, please see the "Didn't find your organization?" note at the bottom of the Globus login page.
4. Finally, if this is your first time signing in, you'll need to choose a username which will complete your account creation.

At this point, our team will need to review and approve your account before you'll have permission to perform certain tasks. If you your account is not approved within 72 hours or you have special requirements, please [Contact us](/docs/contact-us) so that we can help perform any account configuration.

# Next steps

Once your account is approved, you will have scheduling access and protected data browsing in the portal for nodes we've assigned to your account.

For CLI tools and SSH access to nodes, please go to __Portal → Your Account → Access Creds__ and follow the __Update SSH Public Keys__ and __Finish Setup for Node Access__ instructions.

---
sidebar_position: 7
---

# Building your own Waggle device

Are you a professor that wants to use affordable Waggle devices to teach students interested in AI? Are you someone interested in developing a new [edge app](./edge-apps/1-intro-to-edge-apps.md) using a local development platform? Are you a Waggle user interested in using a new sensor (i.e. a new camera, a bat signal detector, a custom sensor they built)? If you would like to build, design and deploy software that could answer your questions above, then Waggle is the right choice for you.

This tutorial will guide you in preparing your own Waggle device and (optionally) registering it to upload data to a shared [development Beehive](../about/architecture.md#beehive). This Waggle device is a fully unlocked development platform running the same [WES infrastructure](../about/architecture.md#waggle-edge-stack-wes) that runs in production Waggle edge devices (ex. the [Wild Waggle Node](../about/architecture.md#wild-sage-node-wild-waggle-node)). This is an ideal platform for users interested in developing a new [edge app](./edge-apps/1-intro-to-edge-apps.md) and/or experimenting with a [new sensor](./access-waggle-sensors.md#bring-your-own-sensor-to-waggle).

## Getting Started

To get started in boot-strapping your Waggle Edge Computing kit you can follow the instructions for the various supported platforms on the [node-platforms](https://github.com/waggle-sensor/node-platforms) GitHub page.

> We currently support a limited set of hardware platform because making edge devices into Waggle requires some hardware specific instructions. Check out [the platforms](https://github.com/waggle-sensor/node-platforms#supported-platforms) we support as of now. More platforms will be added in the future. However, if you would like to add support for other platforms go ahead and submit a [pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) to [node-platforms](https://github.com/waggle-sensor/node-platforms).

### Registering your Waggle device

During the bootstrapping process you will have the option to register your device within the web portal [here](https://portal.sagecontinuum.org/account/dev-devices). It is highly recommended to register your device, as this enables all the core [WES tools](../about/architecture.md#waggle-edge-stack-wes) to be automatically downloaded, enabling the edge app development and run-time environment. Additionally, this enables your edge apps to publish data to the development [Beehive](../about/architecture.md#beehive), accessible to cloud-based analysis tools and workflow frameworks.

To register your device, use the [dev devices form](https://portal.sagecontinuum.org/account/dev-devices). Enter your device ID (which you will obtain through the hardware boot-strapping process) then click "Get Keys" button. A "registration zip" file will be generated and available for download. Then follow the instructions for [your device](https://github.com/waggle-sensor/node-platforms) to load the registration keys.

<!---
![Figure 1: Registering my devices](./images/sage-my-devices.png)
-->

> You may register as many times as you want. But note that each registration key has a short expiration time and should be used shortly after generation.

Now you are ready to develop your edge apps and/or introduce new sensors to the Waggle platform. Head over to the [overview](../about/overview.md) to find the instructions you need for development.

---
sidebar_position: 3
---

# Submit your job

Are you ready to deploy your plugins to measure the world? We will use [edge scheduler](../about/architecture.md#edge-scheduler-es) to submit a job and demonstrate how you can deploy plugins to field-deployed Waggle nodes.

:::caution
If you have not created your account, please go to [https://portal.sagecontinuum.org](https://portal.sagecontinuum.org) and sign in to create a new account with your email. Once signed in, you will be able to create and edit your jobs, but will need a permission to submit jobs to the scheduler. Please [contact-us](../contact-us.md) to request for the job submission permission.
:::

Jobs are an instance of a science goal. They detail what needs to be accomplished on Waggle nodes. A science goal may have multiple jobs to fill the missing data to answer scientific questions of the goal. A job describes,
- [plugins](../about/architecture.md#what-is-a-plugin) that are registered and built in [edge code repository](../about/architecture.md#edge-code-repository-ecr) with specification including any plugin arguments,
- a list of Waggle nodes on which the plugins will be scheduled and run,
- science rules describing a condition-action set that includes when the plugins should be scheduled,
- conditions to determine when the job is considered as completed

Creating and submitting jobs are an important step for successful science mission using Waggle nodes.

## Create a job

We create a job file in YAML format (JSON format is also supported. Please check out [details of job attributes](https://github.com/waggle-sensor/edge-scheduler/tree/main/docs/sesctl).)

```bash
cat << EOF > myjob.yaml
---
name: myjob
plugins:
- name: image-sampler
  pluginSpec:
    image: registry.sagecontinuum.org/theone/imagesampler:0.3.0
    args:
    - -stream
    - bottom_camera
nodes:
  W023:
scienceRules:
- "schedule(image-sampler): cronjob('image-sampler', '* * * * *')"
successcriteria:
- WallClock(1d)
EOF
```

In this example, we want to schedule a plugin named `image-sampler` to collect an image from the camera named `bottom_camera` on `W023` node. As a result of the job execution, we will get images from the node's camera. The job also specifies that the plugin needs to be scheduled every minute (i.e., `* * * * *` in [crontab expression](https://crontab.guru/)). The job completes 24 hours after the job started to run on the node.

:::info
We support human-friendly names for the sensors we host. The "bottom_camear" is named based on the orientation the camera is attached to the node. The full list of sensors including cameras for the `W023` node can be found [here](https://auth.sagecontinuum.org/manifests/w023/)
:::

:::note
We currently do not check job's success criteria. This means that once a job is submitted it is served forever. We will update our system to support different conditions for the success criteria attribute.
:::

## Upload your job to the scheduler

`sesctl` is a command-line tool to manage jobs in the scheduler. You can download the latest version from our [Github repository](https://github.com/waggle-sensor/edge-scheduler/releases). Please make sure you download the tool supported for your machine. For example, on Linux desktop or laptop you would download linux-amd64 version of the tool. Please see the [sesctl document](https://github.com/waggle-sensor/edge-scheduler/tree/main/docs/sesctl#readme) for more details.

:::note
Once you have [contacted us](../contact-us.md) for access permissions, you will need a token provided from [the access page](https://portal.sagecontinuum.org/account/access). Replace the `<<user token>>` below with the access token provided on this page.
:::

You can set the SES host and user token as an environmental variable to your terminal. Please follow your shell's guidance to set them properly. In Bash shell,
```bash
export SES_HOST=https://es.sagecontinuum.org
export SES_USER_TOKEN=<<user token>>
```

Let's ping the scheduler in the cloud,
```bash
sesctl ping
```

You will get a response "pong" from the scheduler,
```
{
 "id": "Cloud Scheduler (cloudscheduler-sage)",
 "version": "0.18.0"
}
```

To create a job using the job file,
```bash
sesctl create --file-path myjob.yaml
```

The scheduler will return a job id and the state for the job creation,
```bash
{
 "job_id": "56",
 "job_name": "myjob",
 "state": "Created"
}
```

To verify that we have uploaded the job,
```bash
sesctl stat
```

You will see the job entry from the response of the command,
```bash
JOB_ID  NAME                         USER       STATUS     AGE
====================================================================
...
56      myjob                        theone     Created    -
...
```

## Submit the job

To submit the job,

```bash
sesctl submit --job-id 56
```

The response should indicate that the job state is changed to "Submitted",
```bash
{
 "job_id": "56",
 "state": "Submitted"
}
```

:::note
You may receive a list of errors from the scheduler if the job fails to be validated. For instance, your account may not have scheduling permission on the node `W023`. Please consult with us for any error, especially errors related to scheduling permission on nodes in the job.
:::

## Check status of jobs
We check status of the job we submitted,
```bash
sesctl stat --job-id 56
```

The tool will print details of the job,
```bash
===== JOB STATUS =====
Job ID: 56
Job Name: myjob
Job Owner:
Job Status: Submitted
Job Starttime: 2022-10-10 02:21:37.373437 +0000 UTC

===== SCHEDULING DETAILS =====
Science Goal ID: 45afe963-5b8b-4e15-654c-54e2946f2ddb
Total number of nodes 1
```

The job status can be also shown in [job status page](https://portal.sagecontinuum.org/job-status).

## [Access to data](./access-waggle-sensors.md)

A few minutes later, the `W023` Waggle node would start collecting images by scheduling the plugin on the node. Collected images are transferred to [Beehive](../about/architecture.md#beehive) for users to download.

```console
curl -H 'Content-Type: application/json' https://data.sagecontinuum.org/api/v1/query -d '
{
    "start": "-5m",
    "filter": {
        "task": "image-sampler",
        "vsn": "W023",
        "name": "upload"
    }
}
'
```

## Clean it up
As we approach to the end of this tutorial, we need to clean up the job because otherwise it will be served forever. To remove the job from the scheduler,
```bash
# since the job is running, we remove the job forcefully
sesctl rm --force 56
```

You should see output that looks like,
```bash
{
 "job_id": "56",
 "state": "Removed"
}
```

## More tutorials using _sesctl_

More tutorials can be found in our [Github repository](https://github.com/waggle-sensor/edge-scheduler/tree/main/docs/sesctl).

## Creating job description with advanced science rules for supporting realistic science mission
The science rule used in the tutorial asked the scheduler to schedule the image sampler plugin every minute. For collecting training images from a set of Waggle nodes this makes total sense with the science rule. However, users in Waggle should want more complex behaviors at the node to not only schedule plugins, but enable cloud computation triggered by sending local events to the cloud. The events and triggers can be captured by creating science rules that monitor local sensor measurement on nodes. Please visit the [science rules](https://github.com/waggle-sensor/edge-scheduler/blob/main/docs/sciencerules/README.md) to know more complex science rules that user can create.

---
sidebar_position: 1
---

# Part 1: Intro to edge apps

## What are edge apps?

Edge apps are programs which read data (ex. sensors, audio, video), process it and then publish information derived from that data.

A basic example of an app is one which reads and publishes a value from a sensor every minute. A more complex example could publish the number of birds in a scene using a deep learning model.

![Basic App](./images/plugin-basic.svg)

Edge apps are composed of code, dependencies and models which are packaged so they can be scheduled on Waggle nodes. At a high level, the typical app lifecycle is:

![Running App](./images/plugin-run.svg)

## Exploring existing edge apps

One of the major goals of Waggle is to provide the science community with a diverse catalog of edge apps to enable the sharing of new research. This catalog is maintained as part of the [Edge Code Repository](https://portal.sagecontinuum.org) where you can find more background information and links to their source repos.

We encourage users to explore the [ECR](/docs/about/architecture#edge-code-repository-ecr) to get familiar with existing apps as well a references if you develop your own edge app.

## Next steps

If this sounds exciting and you'd like to write you own edge app, please continue to [part 2](creating-an-edge-app)!

---
sidebar_position: 2
---

# Part 2: Creating an edge app

In [part 1](intro-to-edge-apps), we showed an overview of what edge apps are and how they fit into the Waggle ecosystem. Now, we'll dive right in and start writing our very own edge app!

## Prerequisites

For this part of the tutorial, we'll assume you are developing directly on a laptop or machine with a camera or webcam available. You should have some basic development experience in [Python](https://www.python.org) and with [git](https://git-scm.com) for version control.

## Development workflow

In the next few parts of this tutorial, we'll deep dive into the following app development workflow:

![App Workflow](./images/plugin-workflow.svg)

First, **data and model selection** is where you scope the problem and identify a new or existing model for your application. This typically happens _outside_ of our ecosystem.

Second, **develop and test** is where you begin to integrate your initial code with our ecosystem, test and finally build your application in [ECR](/docs/about/architecture#edge-code-repository-ecr).

Finally, **deploy and iterate** is where you schedule your application for deployment and look at the results.

## A driving example

In order to illustrate progress through each of these stages, we'll start with a concrete code example and iterate on it over the next few sections.

In practice, _lots_ of work goes into the data and model selection step. For now, we'll assume that groundwork has already been done and we've settled on the following code snippit to start with.

```python
import numpy as np
import cv2


def compute_mean_color(image):
    return np.mean(image, (0, 1)).astype(float)


def main():
    # read example image from file
    image = cv2.imread("example.jpg")

    # compute mean color
    mean_color = compute_mean_color(image)

    # print mean color
    print(mean_color)


if __name__ == "__main__":
    main()
```

## Bootstrapping our app from a template

We'll start our by using a cookiecutter template to bootstrap our app.

First, ensure the latest cookiecutter is installed:

```sh
pip3 install --upgrade cookiecutter
```

Now, run the following command:

```sh
cookiecutter gh:waggle-sensor/cookiecutter-sage-app
```

You should be prompted to fill in the following fields:

```txt
  [1/5] name (my-amazing-app-name): my-amazing-app-name
  [2/5] description (My really amazing app!):
  [3/5] author (My name):
  [4/5] version (0.1.0):
  [5/5] Select kind
    1 - vision
    2 - usbserial_sensor
    3 - minimal
    4 - tutorial                    <<< use 4 for tutorial
    Choose from [1/2/3/4] (1): 4
```

If this succeeds, a new `app-tutorial` directory will be created with the following files:

| Name | Description |
|------|-------------|
| main.py | Main code |
| requirements.txt | Code dependencies |
| Dockerfile | App build instructions |
| sage.yaml | App metadata |

### Installing the dependencies

The first step in preparing our example for the edge is to install [pywaggle](https://github.com/waggle-sensor/pywaggle) in our local development environment.

pywaggle is our Python SDK which provides edge apps access to devices (ex. cameras and microphones) and messaging within a node.

![Accessing Devices](../images/access_to_sensors.svg)

For this tutorial, we'll install the latest version of the requirements included in the template:

```sh
pip3 install --upgrade --requirement requirements.txt
```

### Accessing a camera

Now that we have pywaggle, the first change we'll make is to use a camera as input rather than a static image file. We'll use the following `shapshot()` function to take an RGB snapshot from the camera.

```python
import numpy as np

from waggle.data.vision import Camera


def compute_mean_color(image):
    return np.mean(image, (0, 1)).astype(float)


def main():
    # open camera and take snapshot
    with Camera() as camera:
        snapshot = camera.snapshot()

    # compute mean color
    mean_color = compute_mean_color(snapshot.data)

    # print mean color
    print(mean_color)


if __name__ == "__main__":
    main()
```

Now, we can try this out by running:

```sh
python3 main.py
```

You should see output like:

```txt
[51.43575738 51.83611871 54.64226671]
```

_You're exact numbers may differ as this is computed using your default camera._

### Publishing results

The next change we'll make is to publish our data to the [Beehive Data Repository](/docs/about/architecture#data-repository-dr) instead of just print it. This will allow it to be sent to a Beehive once it's scheduled on a node.

```python
import numpy as np

from waggle.plugin import Plugin
from waggle.data.vision import Camera


def compute_mean_color(image):
    return np.mean(image, (0, 1)).astype(float)


def main():
    with Plugin() as plugin:
        # open camera and take snapshot
        with Camera() as camera:
            snapshot = camera.snapshot()

        # compute mean color
        mean_color = compute_mean_color(snapshot.data)

        # publish mean color
        plugin.publish("color.mean.r", mean_color[0], timestamp=snapshot.timestamp)
        plugin.publish("color.mean.g", mean_color[1], timestamp=snapshot.timestamp)
        plugin.publish("color.mean.b", mean_color[2], timestamp=snapshot.timestamp)


if __name__ == "__main__":
    main()
```

Now, we'll run this using:

```sh
python3 main.py
```

You may notice something... there's no output! Usually, published data is sent to a beehive where it can be viewed later. However, because we're developing locally and have not configured a beehive, the data isn't going anywhere. In the next section, we'll see how we can tap into our published data.

### Viewing run logs

In order to make developing and debugging apps easier, pywaggle can write out a log directory as follows:

```sh
export PYWAGGLE_LOG_DIR=test-run
python3 main.py
```

This will create a new directory named `test-run` and will contain a file named `data.ndjson` which contains something like:

```json
{"meta":{},"name":"color.mean.r","timestamp":"2022-08-23T13:38:04.619466000","value":32.67932074652778}
{"meta":{},"name":"color.mean.g","timestamp":"2022-08-23T13:38:04.619466000","value":19.087491319444446}
{"meta":{},"name":"color.mean.b","timestamp":"2022-08-23T13:38:04.619466000","value":10.337491319444444}
```

If we run `python3 main.py` again, then we'll see new data appended to that file:

```json
{"meta":{},"name":"color.mean.r","timestamp":"2022-08-23T13:38:04.619466000","value":32.67932074652778}
{"meta":{},"name":"color.mean.g","timestamp":"2022-08-23T13:38:04.619466000","value":19.087491319444446}
{"meta":{},"name":"color.mean.b","timestamp":"2022-08-23T13:38:04.619466000","value":10.337491319444444}
{"meta":{},"name":"color.mean.r","timestamp":"2022-08-23T13:38:19.719910000","value":30.90709743923611}
{"meta":{},"name":"color.mean.g","timestamp":"2022-08-23T13:38:19.719910000","value":16.61302517361111}
{"meta":{},"name":"color.mean.b","timestamp":"2022-08-23T13:38:19.719910000","value":8.565154079861111}
```

This provides a convenient way to understand the behavior of an app, particularly one with a more complicated flow.

### Uploading a snapshot

Finally, the last change we'll make is to upload our snapshots after publishing the mean color.

We'll upload every snapshot for demonstration purposes, but you wouldn't want to do this in a real app. Instead, you'd typically upload in response to detecting an event such as an anomalous object or loud noise.

```python
import numpy as np

from waggle.plugin import Plugin
from waggle.data.vision import Camera


def compute_mean_color(image):
    return np.mean(image, (0, 1)).astype(float)


def main():
    with Plugin() as plugin:
        # open camera and take snapshot
        with Camera() as camera:
            snapshot = camera.snapshot()

        # compute mean color
        mean_color = compute_mean_color(snapshot.data)

        # publish mean color
        plugin.publish("color.mean.r", mean_color[0], timestamp=snapshot.timestamp)
        plugin.publish("color.mean.g", mean_color[1], timestamp=snapshot.timestamp)
        plugin.publish("color.mean.b", mean_color[2], timestamp=snapshot.timestamp)

        # save and upload image
        snapshot.save("snapshot.jpg")
        plugin.upload_file("snapshot.jpg", timestamp=snapshot.timestamp)


if __name__ == "__main__":
    main()
```

Let's run our app again using:

```sh
export PYWAGGLE_LOG_DIR=test-run
python3 main.py
```

If you take a look in the `test-run/uploads` directory, you should now see an image.

Uploads are added to the run log directory using the format `nstimestamp-filename`.

You should also see a corresponding item in the `data.ndjson` file.

```json
{"meta":{},"name":"color.mean.r","timestamp":"2022-08-23T13:39:34.985679000","value":29.601871744791666}
{"meta":{},"name":"color.mean.g","timestamp":"2022-08-23T13:39:34.985679000","value":16.004838324652777}
{"meta":{},"name":"color.mean.b","timestamp":"2022-08-23T13:39:34.985679000","value":8.217218967013888}
{"meta":{"filename":"snapshot.jpg"},"name":"upload","timestamp":"2022-08-23T13:39:34.985679000","value":"/Users/sean/dev/pw-example/test-run/uploads/1661279974985679000-snapshot.jpg"}
```

### Tools for analyzing run logs (Optional)

If you find yourself working with run logs frequently, we recommend the [Sage data client](https://pypi.org/project/sage-data-client/) which provides convenient functionality for loading and doing analysis on the `data.ndjson` file. See the ["Load results from file" example](https://github.com/sagecontinuum/sage-data-client#load-results-from-file) for more info.

## Next steps

Congratulations! You've finished preparing our example code for the edge!

In the [part 3](testing-an-edge-app), we'll look at how we can build and test our app on a real node!

---
sidebar_position: 3
---

# Part 3: Testing an edge app

In the [previous part](creating-an-edge-app), we took a code snippit and iterated on it until it was ready for the edge. By the end, we had basic camera access and publishing working!

Now, we're ready to start testing it on a development node and describing our build steps.

## Accessing development nodes

The first thing we need to do is get access to a development node. Unfortunately, we are still developing the infrastructure to open this up to general users.

For now, please [contact us](/docs/contact-us) to request access to a development node and we'll work with you to setup access.

## Creating a repo for our app

Before connecting to our node, let's take a moment to organize our code into a repo we will later use on the node.

Go ahead and create a new Github repo named `app-tutorial` and commit the files from [previous part](creating-an-edge-app).

## Building our app

Now that we've setup node access, ssh to the node then clone and cd into your `app-tutorial` repo:

```sh
git clone https://github.com/username/app-tutorial
cd app-tutorial
```

The first thing we'll do is build our app on the node:

```sh
sudo pluginctl build .
```

This may take some time, but once it completes you should see something like:

```txt
Sending build context to Docker daemon  59.39kB
Step 1/6 : FROM waggle/plugin-base:1.1.1-base
...
Step 2/6 : WORKDIR /app
...
Step 3/6 : COPY requirements.txt .
...
Step 4/6 : RUN pip3 install --no-cache-dir -r requirements.txt
...
Step 5/6 : COPY . .
...
Step 6/6 : ENTRYPOINT ["python3", "main.py"]
...
b38bc0a208d0: Pushed
1101ffccd70a: Pushed
latest: digest: sha256:7bee2a62fbcc9913f1c53bbdab79e973e70947618ffe4db90cae6a8f0ff6c8d7 size: 2407
Successfully built plugin

10.31.81.1:5000/local/app-tutorial
```

Once we see `Successfully built plugin`, we can continue to running our app.

## Running our app

When we successfully built our app, the last line of output was `10.31.81.1:5000/local/app-tutorial`. We will
now use this reference to run our app.

```sh
sudo pluginctl run --name app-tutorial 10.31.81.1:5000/local/app-tutorial
```

When you run this, you'll see that there's a bug in the code:

```sh
Launched the plugin app-tutorial-1659971085 successfully
INFO: 2022/08/08 15:04:45 run.go:63: Plugin is in "Pending" state. Waiting...

[ WARN:0@0.032] global /io/opencv/modules/videoio/src/cap_v4l.cpp (902) open VIDEOIO(V4L2:/dev/video0): can't open camera by index
Traceback (most recent call last):
  File "main.py", line 32, in <module>
    main()
  File "main.py", line 15, in main
    with Camera() as camera:
  File "/usr/local/lib/python3.8/dist-packages/waggle/data/vision.py", line 107, in __enter__
    self.capture.__enter__()
  File "/usr/local/lib/python3.8/dist-packages/waggle/data/vision.py", line 133, in __enter__
    raise RuntimeError(f"unable to open video capture for device {self.device!r}")
RuntimeError: unable to open video capture for device 0
```

This was caused by the fact that most nodes have multiple cameras, so we need to be more specific about which camera to use.

To address this, we'll change the following line in `main.py` from:

```python
        with Camera() as camera:
```

to:

```python
        with Camera("left") as camera:
```

_The specific camera name will depend on your specific node. If you are having problems accessing a camera, please [contact us](/docs/contact-us) for more details._

After rebuilding and running this again, the plugin should run and exit cleanly:

```txt
Launched the plugin app-tutorial-1659971085 successfully
INFO: 2022/08/08 15:04:45 run.go:63: Plugin is in "Pending" state. Waiting...
# should exit cleanly with no output
```

Now that we know this works, please commit and push the change to the repo from your machine.

Finally, if you are rebuilding and running code frequently, you can combine the build and run into a single step as follows:

```sh
sudo pluginctl run --name app-tutorial $(sudo pluginctl build .)
```

## Viewing our output

We'll close this part, by looking at the data we just published. To do this, we'll query the [Beehive Data Repository](/docs/about/architecture#data-repository-dr):

```sh
curl -s 'Content-Type: application/json' https://data.sagecontinuum.org/api/v1/query -d '
{
    "start": "-5m",
    "filter": {
        "task": "app-tutorial"
    }
}'
```

You should see some results like:

```json
{"timestamp":"2022-08-08T15:04:48.820981933Z","name":"color.mean.b","value":133.61671793619792,"meta":{"host":"000048b02d15bdc2.ws-nxcore","job":"Pluginctl","node":"000048b02d15bdc2","plugin":"app-tutorial","task":"app-tutorial","vsn":"W02F"}}
{"timestamp":"2022-08-08T15:04:48.820981933Z","name":"color.mean.g","value":136.46639404296874,"meta":{"host":"000048b02d15bdc2.ws-nxcore","job":"Pluginctl","node":"000048b02d15bdc2","plugin":"app-tutorial","task":"app-tutorial","vsn":"W02F"}}
{"timestamp":"2022-08-08T15:04:48.820981933Z","name":"color.mean.r","value":134.48696818033855,"meta":{"host":"000048b02d15bdc2.ws-nxcore","job":"Pluginctl","node":"000048b02d15bdc2","plugin":"app-tutorial","task":"app-tutorial","vsn":"W02F"}}
{"timestamp":"2022-08-08T15:04:48.820981933Z","name":"upload","value":"https://storage.sagecontinuum.org/api/v1/data/Pluginctl/sage-app-tutorial-app-tutorial/000048b02d15bdc2/1659971088820981933-snapshot.jpg","meta":{"filename":"snapshot.jpg","host":"000048b02d15bdc2.ws-nxcore","job":"Pluginctl","node":"000048b02d15bdc2","plugin":"app-tutorial","task":"app-tutorial","vsn":"W02F"}}
```

These are exactly the mean color values we computed and published!

This is intended to be a quick preview of how to access data to help get you started. If you are interested, we cover this topic in much depth [here](../accessing-data).

## Next steps

Now we've been able to build, run and even fix a bug in our code! In [part 4](publishing-to-ecr), we'll see how to publish a first release of our code to the Edge Code Repository!

---
sidebar_position: 4
---

# Part 4: Publishing to ECR

Now that we've finished [preparing our code](creating-an-edge-app) and [testing it](testing-an-edge-app), we're almost ready to publish it to the [Edge Code Repository](https://portal.sagecontinuum.org)!

## Preparing our app

Before publishing an app to the [Edge Code Repository](/docs/about/architecture#edge-code-repository-ecr), we need to add a few packaging items to it.

First, update the homepage in your `sage.yaml` to point to your `app-tutorial` Github repo and verify that it matches the following:

```yaml
name: "app-tutorial"
version: "0.1.0"
description: "My really amazing app!"
keywords: ""
authors: "Your name"
collaborators: ""
funding: ""
license: ""
homepage: "https://github.com/username/app-tutorial"
source:
  architectures:
    - "linux/amd64"
    - "linux/arm64"
```

Next, create an `ecr-meta` directory in your repo and populate it with the following text and media:

* `ecr-science-description.md` - Markdown with in depth description of the science being done here (1 page of text).
* `ecr-icon.jpg` - An icon for the project/work 512x512px.
* `ecr-science-image.jpg` - A science image for the project with a minimum size of 1920x1080px.

Once we've commited and pushed those files to your repo, we're ready to publish our app!

## Publishing our app

Please visit the [Edge Code Repository](https://portal.sagecontinuum.org) and complete the following steps:

1. Go to "Sign In" and follow the instructions.
2. Go to "My Apps".
3. Go to "Create app" and follow the instructions.

If everything is successful, your plugin will appeared and be marked as "Built".

## Conclusion

Congratulation! You've successfully written, tested and published an app to ECR!

We encourage you to check out other apps in the [ECR](https://portal.sagecontinuum.org) and explore additional functionality provided by [pywaggle](https://github.com/waggle-sensor/pywaggle).


# Sage Data Client

This is the official Sage Python data API client. Its main goal is to make writing queries and working with the results easy. It does this by:

1. Providing a simple query function which talks to the data API.
2. Providing the results in an easy to use [Pandas](https://pandas.pydata.org) data frame.

## Installation

Sage Data Client can be installed with pip using:

```sh
pip3 install sage-data-client
```

If you prefer to install this package into a Python virtual environment or are unable to install it system wide, you can use the [venv](https://docs.python.org/3/library/venv.html) module as follows:

```sh
# 1. Create a new virtual environment called my-venv.
python3 -m venv my-venv

# 2. Activate the virtual environment
source my-venv/bin/activate

# 3. Install sage data client in the virtual environment
pip3 install sage-data-client
```

Note: If you are using Linux, you may need to install the `python3-venv` package which is outside of the scope of this document.

Note: You will need to activate this virtual environment when opening a new terminal before running any Python scripts using Sage Data Client.

## Usage Examples

### Query API

```python
import sage_data_client

# query and load data into pandas data frame
df = sage_data_client.query(
    start="-1h",
    filter={
        "name": "env.temperature",
    }
)

# print results in data frame
print(df)

# meta columns are expanded into meta.fieldname. for example, here we print the unique nodes
print(df["meta.vsn"].unique())

# print stats of the temperature data grouped by node + sensor.
print(df.groupby(["meta.vsn", "meta.sensor"]).value.agg(["size", "min", "max", "mean"]))
```

```python
import sage_data_client

# query and load data into pandas data frame
df = sage_data_client.query(
    start="-1h",
    filter={
        "name": "env.raingauge.*",
    }
)

# print number of results of each name
print(df.groupby(["meta.vsn", "name"]).size())
```

### Load results from file

If we have saved the results of a query to a file `data.json`, we can also load using the `load` function as follows:

```python
import sage_data_client

# load results from local file
df = sage_data_client.load("data.json")

# print number of results of each name
print(df.groupby(["meta.vsn", "name"]).size())
```

### Integration with Notebooks

Since we leverage the fantastic work provided by the Pandas library, performing things like looking at dataframes or creating plots is easy.

A basic example of querying and plotting data can be found [here](https://github.com/sagecontinuum/sage-data-client/blob/main/examples/plotting_example.ipynb).

### Additional Examples

Additional code examples can be found in the [examples](https://github.com/sagecontinuum/sage-data-client/tree/main/examples) directory.

If you're interested in contributing your own examples, feel free to add them to [examples/contrib](https://github.com/sagecontinuum/sage-data-client/tree/main/examples/contrib) and open a PR!

## Reference

The `query` function accepts the following arguments:

* `start`. Absolute or relative start timestamp. (**required**)
* `end`. Absolute or relative end timestamp.
* `head`. Limit results to `head` earliest values per series. (Only one of `head` or `tail` can be provided.)
* `tail`. Limit results to `tail` latest values per series. (Only one of `head` or `tail` can be provided.)
* `filter`. Key-value patterns to filter data on.

"""
This example demonstrates one approach for combining multiple queries by resampling
results into 30 minute windows and merging those into a new data frame.
"""
import sage_data_client
import pandas as pd


def join_resampled_queries(start, end, window, filters):
    """
    join_resampled_queries joins resampled data for a set of filters together
    into a single data frame
    """
    return pd.DataFrame({
        name: sage_data_client.query(
            start=start,
            end=end,
            filter=filter,
        ).resample(window, on="timestamp").value.mean()
        for name, filter in filters.items()
    })


def main():
    start = "2022-01-10T00:00:00Z"
    end = "2022-01-11T00:00:00Z"
    vsn = "W023"

    # combine lat, lon, temperature, pressure and humidity into data frame
    df = join_resampled_queries(start, end, "30min", {
        "lat": {
            "name": "sys.gps.lat",
            "vsn": vsn,
        },
        "lon": {
            "name": "sys.gps.lon",
            "vsn": vsn,
        },
        "temperature": {
            "name": "env.temperature",
            "vsn": vsn,
            "sensor": "bme680"
        },
        "pressure": {
            "name": "env.pressure",
            "vsn": vsn,
            "sensor": "bme680"
        },
        "humidity": {
            "name": "env.relative_humidity",
            "vsn": vsn,
            "sensor": "bme680"
        },
    })

    # print out data for quick inspection
    print(df)

    # save data to csv
    df.to_csv("combined.csv")


if __name__ == "__main__":
    main()

"""
This example is a skeleton of how to poll the data system every minute for unusual
pressure events.

In this case, events are determined windows with a stddev above an example
threshold. For applications, you will need to provide your own criteria for
events.

Additionally, you will need to provide a specific mechanism to carry out the
alerts (ex. email, Slack, dedicated alerting / ticketing system, etc).
"""
import sage_data_client
import time

while True:
    # query pressure data in recent 10 minute window
    df = sage_data_client.query(
        start="-10m",
        filter={
            "name": "env.pressure",
            "sensor": "bme680",
        }
    )

    # compute stddev for nodes' pressure data in window
    std = df.groupby("meta.vsn").value.std()

    # find all pressure events exceeding an example threshold
    events = std[std > 8.0]

    # "post" vsn to alert system
    for vsn in events.index:
        print(f"post {vsn} to alert system")

    time.sleep(60)

"""
This example demonstrates cross referencing rain gauge data to find rainy images. It outputs a list
of urls which can be saved and downloaded as follows:

python3 print_rain_event_image_urls.py > urls.txt
wget -r -N -i urls.txt
"""
import sage_data_client
import pandas as pd

vsn = "W039"

# query raingauge data for the last week
df = sage_data_client.query(
    start="2021-12-20",
    end="2021-12-27",
    filter={
        "name": "env.raingauge.acc",
        "vsn": vsn,
    }
)

# compute mean rain in hour window
mean_acc = df.resample("1h", on="timestamp").value.mean()

# find rain accumulation events
rain_events = mean_acc[mean_acc > 0]

# collect uploads in each rain event window
uploads = pd.concat(sage_data_client.query(
        start=ts,
        end=ts + pd.to_timedelta("1h"),
        filter={
            "name": "upload",
            "vsn": vsn,
            "task": "imagesampler-top",
        }
    ) for ts in rain_events.index)

# print all urls found
for url in uploads.value.values:
    print(url)


"""
This example demonstrates querying rain gauge data and printing the total
number of measurements grouped by VSN and sensor.
"""
import sage_data_client

# query and load data into pandas data frame
df = sage_data_client.query(
    start="-1h",
    filter={
        "name": "env.raingauge.*",
    }
)

# print number of results of each name
print(df.groupby(["meta.vsn", "name"]).size())


"""
This example demonstrates querying all temperature data and printing basic stats grouped by VSN and sensor.
"""
import sage_data_client

# query and load data into pandas data frame
df = sage_data_client.query(
    start="-1h",
    filter={
        "name": "env.temperature",
    }
)

# print stats of the temperature data grouped by node + sensor.
print(df.groupby(["meta.vsn", "meta.sensor"]).value.agg(["size", "min", "max", "mean"]))

"""
This is an example of a simple edge-to-cloud batch trigger which uses sage-data-client
to gather and aggregate internal temperature data every 5 minutes and prints all
nodes which exceed a threshold.

Although it's simple, this example could easily be extended in multiple ways. For example:
* Instead of just printing, an alert could be posted to Slack.
* Instead of a fixed threshold, the typical value across all nodes could be used to determine outliers.
"""
import sage_data_client
import time


def main():
    filter = {
        "name": "env.temperature",
        "sensor": "bme280",
    }

    threshold = 55.0

    while True:
        # get the last 5m of temperature data
        df = sage_data_client.query(start="-5m", filter=filter)

        # get mean temperature by node in batch query
        mean_temps = df.groupby("meta.vsn").value.mean()

        # print values which exceed threshold
        print(mean_temps[mean_temps > threshold])

        # wait 5m
        time.sleep(300)


if __name__ == "__main__":
    main()

"""
This is an example of a simple edge-to-cloud stream trigger which uses sage-data-client
to watch the latest internal temperature values and print records which exceed a threshold.

Although it's simple, this example could easily be extended in multiple ways. For example:
* Instead of just printing, an alert could be posted to Slack.
* Instead of a fixed threshold, you could learn a moving average per node and flag outliers.

Note: In the future, this kind of streaming functionality *might* be provided by sage-data-client,
but for now you can adapt this example to fit you use case.
"""
import sage_data_client
import pandas as pd
import time


def watch(start=None, filter=None):
    if start is None:
        start = pd.Timestamp.utcnow()

    while True:
        df = sage_data_client.query(
            start=start,
            filter=filter,
        )

        if len(df) > 0:
            start = df.timestamp.max()
            yield df

        time.sleep(3.0)


def main():
    filter = {
        "name": "env.temperature",
        "sensor": "bme280",
    }

    threshold = 50.0

    for df in watch(filter=filter):
        # print values which exceed threshold
        print(df[df.value > threshold].sort_values("timestamp"))


if __name__ == "__main__":
    main()