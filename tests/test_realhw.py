"""Test with real hardware"""
import time
import os
import asyncio

import pytest

from actuonix_lac.blocking import LAC
from actuonix_lac.aio import AsyncLAC

pytestmark = pytest.mark.skipif(not os.environ.get("LACHWTEST"), reason="Must LACHWTEST to test HW")


@pytest.mark.parametrize("expected_position", [16, 256, 32])
def test_blocking_position(expected_position: int) -> None:
    """Test blocking version"""
    servo = LAC()
    position_grace = 4
    servo.set_accuracy(position_grace)
    servo.set_position(expected_position)
    started = time.time()
    while True:
        if time.time() - started > 10:
            raise TimeoutError("Timed out")
        true_position = servo.get_feedback()
        if (expected_position - position_grace) < true_position < (expected_position + position_grace):
            break
        time.sleep(0.1)


@pytest.mark.asyncio
@pytest.mark.parametrize("expected_position", [16, 256, 32])
async def test_async_position(expected_position: int) -> None:
    """Test blocking version"""
    servo = AsyncLAC()
    position_grace = 4
    await servo.set_accuracy(position_grace)
    await servo.set_position(expected_position)

    async def wait_for_position() -> None:
        """Loop until position is what we want"""
        nonlocal expected_position, position_grace
        while True:
            true_position = await servo.get_feedback()
            if (expected_position - position_grace) < true_position < (expected_position + position_grace):
                break
            await asyncio.sleep(0.5)

    await asyncio.wait_for(wait_for_position(), timeout=10)
