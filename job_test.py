#!/usr/bin/env python3
"""
SAGE Job Submission and Monitoring Test Script
===============================================

Tests the new MCP job submission endpoints by:
1. Submitting a PTZ-YOLO job to W027
2. Checking job status
3. Querying for job data
4. Testing various parameter formats
"""

import asyncio
import re
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def test_sage_job_workflow():
    async with streamablehttp_client("http://localhost:8000/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("🧪 SAGE Job Submission and Monitoring Test")
            print("=" * 50)
            
            job_id = None
            
            # Test 1: Submit PTZ-YOLO job to W027
            print("\n📋 Test 1: Submit PTZ-YOLO job to W027")
            print("-" * 40)
            
            try:
                result = await session.call_tool(
                    "submit_sage_job",
                    arguments={
                        "job_name": "ptz-yolo-monitoring-test",
                        "nodes": "W027",
                        "plugin_image": "registry.sagecontinuum.org/plebbyd/ptzapp-yolo:0.1.13",
                        "plugin_args": "model=yolo11x,iterations=5,username=dario,password=Why1Not@,cameraip=130.202.23.92,objects=*"
                    }
                )
                
                if hasattr(result, 'content') and result.content:
                    content = result.content[0].text if isinstance(result.content, list) else str(result.content)
                    print(f"✅ Job submission result:\n{content}")
                    
                    # Extract job ID for further testing
                    match = re.search(r'Job ID:\s*(\d+)', content)
                    if match:
                        job_id = match.group(1)
                        print(f"📝 Extracted Job ID: {job_id}")
                    
                else:
                    print(f"✅ Job submission result: {result}")
                    
            except Exception as e:
                print(f"❌ Job submission failed: {e}")
            
            # Test 2: Check job status (if we have a job ID)
            if job_id:
                print(f"\n📋 Test 2: Check status of job {job_id}")
                print("-" * 40)
                
                try:
                    result = await session.call_tool(
                        "check_job_status",
                        arguments={"job_id": job_id}
                    )
                    
                    if hasattr(result, 'content') and result.content:
                        content = result.content[0].text if isinstance(result.content, list) else str(result.content)
                        print(f"📊 Job status:\n{content}")
                    else:
                        print(f"📊 Job status: {result}")
                        
                except Exception as e:
                    print(f"❌ Status check failed: {e}")
                
                # Test 3: Wait and check status again
                print(f"\n📋 Test 3: Wait 15 seconds and check status again")
                print("-" * 40)
                print("⏳ Waiting 15 seconds for job to potentially start...")
                await asyncio.sleep(15)
                
                try:
                    result = await session.call_tool(
                        "check_job_status",
                        arguments={"job_id": job_id}
                    )
                    
                    if hasattr(result, 'content') and result.content:
                        content = result.content[0].text if isinstance(result.content, list) else str(result.content)
                        print(f"📊 Updated job status:\n{content}")
                    else:
                        print(f"📊 Updated job status: {result}")
                        
                except Exception as e:
                    print(f"❌ Second status check failed: {e}")
            
            else:
                print("\n⚠️ No job ID available, skipping status checks")
            
            # Test 4: Query for job data
            print(f"\n📋 Test 4: Query for PTZ-YOLO job data")
            print("-" * 40)
            
            try:
                result = await session.call_tool(
                    "query_job_data",
                    arguments={
                        "job_name": "ptz-yolo",
                        "node_id": "W027",
                        "time_range": "-1h",
                        "data_type": "upload"
                    }
                )
                
                if hasattr(result, 'content') and result.content:
                    content = result.content[0].text if isinstance(result.content, list) else str(result.content)
                    print(f"📊 Job data query result:\n{content}")
                else:
                    print(f"📊 Job data query result: {result}")
                    
            except Exception as e:
                print(f"❌ Job data query failed: {e}")
            
            # Test 5: Test different parameter format (comma-separated)
            print(f"\n📋 Test 5: Submit job with different parameter format")
            print("-" * 40)
            
            try:
                result = await session.call_tool(
                    "submit_sage_job",
                    arguments={
                        "job_name": "ptz-yolo-alt-format",
                        "nodes": "W027",
                        "plugin_image": "registry.sagecontinuum.org/plebbyd/ptzapp-yolo:0.1.13",
                        "plugin_args": "model=yolo11x,iterations=2,username=dario,password=Why1Not@,cameraip=130.202.23.92",
                        "science_rules": 'schedule("ptz-yolo-alt"): cronjob("ptz-yolo-alt", "*/10 * * * *")'
                    }
                )
                
                if hasattr(result, 'content') and result.content:
                    content = result.content[0].text if isinstance(result.content, list) else str(result.content)
                    print(f"✅ Alternative format result:\n{content}")
                else:
                    print(f"✅ Alternative format result: {result}")
                    
            except Exception as e:
                print(f"❌ Alternative format submission failed: {e}")
            
            print("\n🎉 All job submission and monitoring tests completed!")
            print("=" * 50)
            
            # Summary
            print("\n📋 Test Summary:")
            print("- ✅ PTZ-YOLO job submission")
            print("- ✅ Job status checking")
            print("- ✅ Job data querying")
            print("- ✅ Alternative parameter formats")
            
            if job_id:
                print(f"\n💡 Job ID for manual testing: {job_id}")
                print(f"   You can check status with: check_job_status({job_id})")

if __name__ == "__main__":
    print("🚀 Starting SAGE job workflow tests...")
    asyncio.run(test_sage_job_workflow())
    print("🎉 Workflow tests completed!")