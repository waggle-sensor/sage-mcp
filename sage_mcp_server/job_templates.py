from typing import List
from .models import SageJob, PluginSpec, PluginArguments, SelectorRequirements, CameraSageJob

class JobTemplates:
    """Predefined job templates for common SAGE jobs"""
    
    @staticmethod
    def image_sampler(
        job_name: str,
        nodes: List[str],
        interval_mins: int = 10,
        width: int = 1920,
        height: int = 1080
    ) -> SageJob:
        plugin_name = "image-sampler"
        plugin = PluginSpec(
            name=plugin_name,
            image=f"waggle/plugin-image-sampler:0.2.0",
            args=PluginArguments(args_dict={
                "width": width,
                "height": height
            }),
            selector=SelectorRequirements(gpu=None, camera=True, usb=None)
        )
        science_rule = f'schedule("{plugin_name}"): cronjob("{plugin_name}", "*/{interval_mins} * * * *")'
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )
    
    @staticmethod
    def ptz_sampler(
        job_name: str,
        nodes: List[str],
        interval_mins: int = 15,
        preset_positions: List[int] = [1, 2, 3]
    ) -> SageJob:
        plugin_name = "ptz-sampler"
        position_args = ",".join(map(str, preset_positions))
        plugin = PluginSpec(
            name=plugin_name,
            image=f"waggle/plugin-ptz-sampler:0.3.0",
            args=PluginArguments(args_dict={
                "positions": position_args
            }),
            selector=SelectorRequirements(gpu=None, camera=True, usb=None)
        )
        science_rule = f'schedule("{plugin_name}"): cronjob("{plugin_name}", "*/{interval_mins} * * * *")'
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )
    
    @staticmethod
    def yolo_detector(
        job_name: str,
        nodes: List[str],
        model: str = "yolov5s",
        confidence: float = 0.25,
        interval_mins: int = 10
    ) -> SageJob:
        plugin_name = "yolo-detector"
        plugin = PluginSpec(
            name=plugin_name,
            image=f"waggle/plugin-yolo-detector:0.4.0",
            args=PluginArguments(args_dict={
                "model": model,
                "confidence": confidence
            }),
            selector=SelectorRequirements(gpu=True, camera=True, usb=None)
        )
        science_rule = f'schedule("{plugin_name}"): cronjob("{plugin_name}", "*/{interval_mins} * * * *")'
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )
    
    @staticmethod
    def ptz_yolo(
        job_name: str,
        nodes: List[str],
        iterations: int = 10,
        objects: str = "person,car,truck",
        username: str = "",
        password: str = "",
        camera_ip: str = "",
        pan_step: int = 45,
        tilt: int = 0,
        zoom: int = 1,
        model: str = "yolov8n",
        iter_delay: float = 1.0,
        confidence: float = 0.25
    ) -> SageJob:
        plugin = PluginSpec(
            name=job_name,
            image="plebbyd/ptzapp-yolo:0.1.12",
            args=PluginArguments.from_string(
                f"iterations={iterations},"
                f"objects={objects},"
                f"username={username},"
                f"password={password},"
                f"cameraip={camera_ip},"
                f"panstep={pan_step},"
                f"tilt={tilt},"
                f"zoom={zoom},"
                f"model={model},"
                f"iterdelay={iter_delay},"
                f"confidence={confidence}"
            ),
            selector=SelectorRequirements(gpu=True, camera=True, usb=None)
        )
        return SageJob(name=job_name, nodes=nodes, plugins=[plugin])
    
    @staticmethod
    def air_quality(
        job_name: str,
        nodes: List[str]
    ) -> SageJob:
        plugin = PluginSpec(
            name="air-quality",
            image="registry.sagecontinuum.org/seanshahkarami/air-quality:0.2.0",
            args=PluginArguments(args_dict={"device": "/host/dev/airquality"}),
            selector=SelectorRequirements(
                gpu=None, camera=None, usb=None,
                custom_selectors={"resource.airquality": "true"}
            ),
            privileged=True
        )
        science_rule = 'schedule("air-quality"): True'
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule],
            node_value_format="true",
            success_criteria=["WallClock('1day')"]
        )
    
    @staticmethod
    def mobotix_scan(
        job_name: str,
        nodes: List[str],
        camera_ip: str = "camera-mobotix-thermal",
        mode: str = "direction",
        direction: str = "south",
        angle: str = "15",
        preset_positions: str = "NEH,NEB,NEG,EH,EB,EG,SEH,SEB,SEG,SH,SB,SG,SWH,SWB,SWG",
        username: str = "admin",
        password: str = "meinsm",
        interval_mins: int = 1
    ) -> SageJob:
        plugin = PluginSpec(
            name="mobotix-scan-direction",
            image="registry.sagecontinuum.org/bhupendraraut/mobotix-scan:0.24.8.20",
            args=PluginArguments(args_dict={
                "ip": camera_ip,
                "mode": mode,
                f"-{direction}": angle,
                "pt": preset_positions,
                "u": username,
                "p": password
            }),
            selector=SelectorRequirements(gpu=None, camera=None, usb=None)
        )
        science_rule = f'schedule("mobotix-scan-direction"): cronjob("mobotix-scan-direction", "* * * * *")'
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )
    
    @staticmethod
    def audio_sampler(
        job_name: str,
        nodes: List[str]
    ) -> SageJob:
        plugin = PluginSpec(
            name="audio-sampler",
            image="registry.sagecontinuum.org/seanshahkarami/audio-sampler:0.4.1",
            args=PluginArguments(),
            selector=SelectorRequirements(gpu=None, camera=None, usb=None)
        )
        science_rule = 'schedule(audio-sampler): cronjob("audio-sampler", "*/15 * * * *")'
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )
    
    @staticmethod
    def camera_sampler(
        job_name: str,
        nodes: List[str],
        camera_position: str = "bottom"
    ) -> SageJob:
        plugin_name = f"imagesampler-{camera_position}"
        wget_cmd = f'wget -O ./sample.jpg "http://camera-{camera_position}-rgb-hanwha/stw-cgi/video.cgi?msubmenu=snapshot&action=view"  --user camera --password 0Bscura# && python3 /app/upload.py --name {camera_position}_camera --file-path /sample.jpg'
        plugin = PluginSpec(
            name=plugin_name,
            image="registry.sagecontinuum.org/yonghokim/imagesampler:0.3.7",
            args=PluginArguments(args_dict={"__camera_cmd": wget_cmd}),
            selector=SelectorRequirements(
                gpu=None, camera=None, usb=None,
                custom_selectors={"zone": "core"}
            ),
            entrypoint="/bin/bash"
        )
        science_rule = f'schedule({plugin_name}): cronjob("{plugin_name}", "10 * * * *")'
        job = CameraSageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule],
            node_value_format="null",
            success_criteria=[],
            camera_cmd=wget_cmd,
            camera_plugin_name=plugin_name
        )
        return job
    
    @staticmethod
    def cloud_cover(
        job_name: str,
        nodes: List[str],
        camera_stream: str = "top_camera",
        interval_mins: int = 10
    ) -> SageJob:
        plugin = PluginSpec(
            name="cloud-cover-top",
            image="registry.sagecontinuum.org/seonghapark/cloud-cover:0.1.3",
            args=PluginArguments(args_dict={"stream": camera_stream}),
            selector=SelectorRequirements(gpu=True, camera=None, usb=None)
        )
        science_rule = f'schedule("cloud-cover-top"): cronjob("cloud-cover-top", "*/{interval_mins} * * * *")'
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )
    
    @staticmethod
    def solar_irradiance(
        job_name: str,
        nodes: List[str],
        gps_server: str = "wes-gps-server.default.svc.cluster.local"
    ) -> SageJob:
        plugin = PluginSpec(
            name="solar-irradiance",
            image="registry.sagecontinuum.org/seonghapark/solar-irradiance:0.1.0",
            args=PluginArguments(),
            selector=SelectorRequirements(gpu=None, camera=None, usb=None),
            env={"WAGGLE_GPS_SERVER": gps_server}
        )
        science_rule = 'schedule("solar-irradiance"): True'
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )
    
    @staticmethod
    def sound_event_detection(
        job_name: str,
        nodes: List[str],
        duration_s: int = 5,
        publish: bool = True,
        interval_mins: int = 10
    ) -> SageJob:
        plugin = PluginSpec(
            name="sound-event-detection",
            image="registry.sagecontinuum.org/dariodematties/sound-event-detection:0.1.1",
            args=PluginArguments(args_dict={
                "DURATION_S": str(duration_s),
                "PUBLISH": str(publish).lower()
            }),
            selector=SelectorRequirements(gpu=None, camera=None, usb=None)
        )
        science_rule = f'schedule("sound-event-detection"): cronjob("sound-event-detection", "*/{interval_mins} * * * *")'
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )
    
    @staticmethod
    def avian_diversity_monitoring(
        job_name: str,
        nodes: List[str],
        num_recordings: int = 2,
        sound_interval: int = 30,
        interval_mins: int = 5
    ) -> SageJob:
        plugin = PluginSpec(
            name="avian-diversity-monitoring",
            image="registry.sagecontinuum.org/dariodematties1/avian-diversity-monitoring:0.2.4",
            args=PluginArguments(args_dict={
                "num_rec": str(num_recordings),
                "sound_int": str(sound_interval)
            }),
            selector=SelectorRequirements(gpu=True, camera=None, usb=None)
        )
        science_rule = f'schedule("avian-diversity-monitoring"): cronjob("avian-diversity-monitoring", "*/{interval_mins} * * * *")'
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )
    
    @staticmethod
    def weather_classification(
        job_name: str,
        nodes: List[str],
        lidar_ip: str = "10.31.81.196",
        lidar_password: str = "Halo217_1128",
        interval_mins: int = 60
    ) -> SageJob:
        plugin = PluginSpec(
            name="weather-classification",
            image="registry.sagecontinuum.org/rjackson/weatherclassification:2025.6.20",
            args=PluginArguments(args_dict={
                "IP": lidar_ip,
                "password": lidar_password
            }),
            selector=SelectorRequirements(gpu=True, camera=None, usb=None)
        )
        science_rule = f'schedule("weather-classification"): cronjob("weather-classification", "5 */{interval_mins} * * *")'
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )
    
    @staticmethod
    def waggle_aqt(
        job_name: str,
        nodes: List[str],
        device: str = "/host/dev/waggle-crocus-mux-p4",
        interval_mins: int = 10
    ) -> SageJob:
        plugin = PluginSpec(
            name="waggle-aqt",
            image="registry.sagecontinuum.org/jrobrien/waggle-aqt:0.23.5.04",
            args=PluginArguments(args_dict={"device": device}),
            selector=SelectorRequirements(
                gpu=None, camera=None, usb=None,
                custom_selectors={"zone": "core"}
            ),
            privileged=True
        )
        science_rule = f'schedule("waggle-aqt"): cronjob("waggle-aqt", "*/{interval_mins} * * * *")'
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )
    
    @staticmethod
    def waggle_wxt536(
        job_name: str,
        nodes: List[str],
        device: str = "/host/dev/waggle-crocus-mux-p3",
        interval_mins: int = 10
    ) -> SageJob:
        plugin = PluginSpec(
            name="waggle-wxt536",
            image="registry.sagecontinuum.org/jrobrien/waggle-wxt536:0.24.11.14",
            args=PluginArguments(args_dict={"device": device}),
            selector=SelectorRequirements(
                gpu=None, camera=None, usb=None,
                custom_selectors={"zone": "core"}
            ),
            privileged=True
        )
        science_rule = f'schedule("waggle-wxt536"): cronjob("waggle-wxt536", "*/{interval_mins} * * * *")'
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )
    
    @staticmethod
    def multi_plugin_ml_suite(
        job_name: str,
        nodes: List[str],
        cloud_cover_interval: int = 10,
        sound_event_interval: int = 10,
        avian_monitoring_interval: int = 5,
        cloud_motion_interval: int = 20
    ) -> SageJob:
        plugins = [
            PluginSpec(
                name="cloud-cover-top",
                image="registry.sagecontinuum.org/seonghapark/cloud-cover:0.1.3",
                args=PluginArguments(args_dict={"stream": "top_camera"}),
                selector=SelectorRequirements(gpu=True, camera=None, usb=None)
            ),
            PluginSpec(
                name="solar-irradiance",
                image="registry.sagecontinuum.org/seonghapark/solar-irradiance:0.1.0",
                args=PluginArguments(),
                selector=SelectorRequirements(gpu=None, camera=None, usb=None)
            ),
            PluginSpec(
                name="sound-event-detection",
                image="registry.sagecontinuum.org/dariodematties/sound-event-detection:0.1.1",
                args=PluginArguments(args_dict={"DURATION_S": "5", "PUBLISH": "true"}),
                selector=SelectorRequirements(gpu=None, camera=None, usb=None)
            ),
            PluginSpec(
                name="avian-diversity-monitoring",
                image="registry.sagecontinuum.org/dariodematties1/avian-diversity-monitoring:0.2.4",
                args=PluginArguments(args_dict={"num_rec": "2", "sound_int": "30"}),
                selector=SelectorRequirements(gpu=True, camera=None, usb=None)
            )
        ]
        science_rules = [
            f'schedule("cloud-cover-top"): cronjob("cloud-cover-top", "*/{cloud_cover_interval} * * * *")',
            'schedule("solar-irradiance"): True',
            f'schedule("sound-event-detection"): cronjob("sound-event-detection", "*/{sound_event_interval} * * * *")',
            f'schedule("avian-diversity-monitoring"): cronjob("avian-diversity-monitoring", "*/{avian_monitoring_interval} * * * *")'
        ]
        if cloud_motion_interval > 0:
            science_rules.append(f'schedule("cloud-motion-top"): cronjob("cloud-motion-top", "*/{cloud_motion_interval} * * * *")')
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=plugins,
            science_rules=science_rules
        ) 