import logging
import tempfile
import subprocess
import os
import sys
import json
from models import SageConfig, SageJob

logger = logging.getLogger(__name__)

class SageJobService:
    """Service for submitting and managing SAGE jobs"""
    
    def __init__(self, config: SageConfig):
        self.config = config
    
    def submit_job(self, job: SageJob) -> tuple[bool, str]:
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                job.write_yaml(f.name)
                temp_yaml_path = f.name
            try:
                cmd = ["sesctl", "submit", "--file-path", temp_yaml_path]
                if self.config.dry_run:
                    cmd.append("--dry-run")
                    logger.info("Using --dry-run mode (no actual submission)")
                if self.config.token:
                    cmd.extend(["--token", self.config.token])
                if self.config.server:
                    cmd.extend(["--server", self.config.server])
                logger.info(f"Running command: {' '.join(cmd[:5])} [using configured token]")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    output = result.stdout.strip()
                    logger.info(f"sesctl output: {output}")
                    job_id = None
                    if "job_id" in output:
                        try:
                            response_json = json.loads(output)
                            job_id = response_json.get("job_id")
                        except json.JSONDecodeError:
                            import re
                            match = re.search(r'"?job_id"?\s*:\s*"?(\d+)"?', output)
                            if match:
                                job_id = match.group(1)
                    if job_id:
                        status_msg = "Dry-run completed successfully!" if self.config.dry_run else "Submitted"
                        return True, f"✅ Job {'validated' if self.config.dry_run else 'submitted'} successfully!\nJob ID: {job_id}\nJob Name: {job.name}\nNodes: {', '.join(job.nodes)}\nStatus: {status_msg}\n\nUse check_job_status({job_id}) to monitor progress."
                    else:
                        status_msg = "Dry-run completed!" if self.config.dry_run else "Submitted"
                        return True, f"✅ Job {'validated' if self.config.dry_run else 'submitted'} successfully!\nResponse: {output}\nJob Name: {job.name}\nNodes: {', '.join(job.nodes)}\nStatus: {status_msg}"
                else:
                    error_msg = result.stderr.strip() or result.stdout.strip()
                    if "must provide a valid token" in error_msg:
                        return False, f"❌ Authentication required: Please provide a valid SAGE token.\nError: {error_msg}"
                    return False, f"❌ Job submission failed:\n{error_msg}"
            finally:
                if os.path.exists(temp_yaml_path):
                    os.unlink(temp_yaml_path)
        except Exception as e:
            logger.error(f"Error submitting job: {e}")
            return False, f"❌ Error submitting job: {e}"
    
    def check_job_status(self, job_id: str) -> str:
        try:
            cmd = ["sesctl", "stat", "--job-id", job_id]
            if self.config.token:
                cmd.extend(["--token", self.config.token])
            if self.config.server:
                cmd.extend(["--server", self.config.server])
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                output = result.stdout.strip()
                logger.info(f"Job status output: {output}")
                try:
                    status_json = json.loads(output)
                    return f"📊 Job Status (ID: {job_id}):\n{json.dumps(status_json, indent=2)}"
                except json.JSONDecodeError:
                    return f"📊 Job Status (ID: {job_id}):\n{output}"
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                return f"❌ Error checking job status:\n{error_msg}"
        except Exception as e:
            logger.error(f"Error checking job status: {e}")
            return f"❌ Error checking job status: {e}"
    
    def force_remove_job(self, job_id: str) -> str:
        try:
            cmd = ["sesctl", "rm", "--force", job_id]
            if self.config.token:
                cmd.extend(["--token", self.config.token])
            if self.config.server:
                cmd.extend(["--server", self.config.server])
            logger.info(f"Running force remove command: {' '.join(cmd[:4])} [with token]")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                output = result.stdout.strip()
                return f"✅ Job {job_id} removed successfully!\nOutput: {output}"
            else:
                error_output = result.stderr.strip() or result.stdout.strip()
                logger.error(f"sesctl rm failed with return code {result.returncode}: {error_output}")
                return f"❌ Error removing job {job_id}:\nReturn code: {result.returncode}\nError: {error_output}"
        except Exception as e:
            logger.error(f"Error removing job: {e}")
            return f"❌ Error removing job: {e}"

    def suspend_job(self, job_id: str) -> str:
        try:
            cmd = ["sesctl", "rm", "--suspend", job_id]
            if self.config.token:
                cmd.extend(["--token", self.config.token])
            if self.config.server:
                cmd.extend(["--server", self.config.server])
            logger.info(f"Running suspend command: {' '.join(cmd[:4])} [with token]")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                output = result.stdout.strip()
                return f"⏸️ Job {job_id} suspended successfully!\nOutput: {output}"
            else:
                error_output = result.stderr.strip() or result.stdout.strip()
                logger.error(f"sesctl rm --suspend failed with return code {result.returncode}: {error_output}")
                return f"❌ Error suspending job {job_id}:\nReturn code: {result.returncode}\nError: {error_output}"
        except Exception as e:
            logger.error(f"Error suspending job: {e}")
            return f"❌ Error suspending job: {e}" 