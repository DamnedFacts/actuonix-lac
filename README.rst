============
actuonix-lac
============

Python module for controlling an Actuonix/Firgelli Linear Actuator Control Board (https://www.actuonix.com/LAC-Board-p/lac.htm).

There's both blocking and asyncio variant available, usage::

    from actuonix_lac.blocking import LAC  # The old from actuonix_lac.lac import LAC also works
    sb = LAC()
    sb.set_position(255)
    # wait a moment for the movement to complete
    sb.get_feedback()

or::

    import asyncio
    from actuonix_lac.aio import AsyncLAC
    loop = asyncio.get_event_loop()
    s = AsyncLAC()
    loop.run_until_complete(s.set_position, 500)
    # wait a moment for the movement to complete
    loop.run_until_complete(s.get_feedback())

Obviously when inside an async function just use await instead of loop.run_until_complete.

There is also CLI interface (but due to USB init taking some time you should not use it in loops etc)::

    laccontrol get-position # returns the raw position
    laccontrol set-position 316 # sets target position to 316

Remember that you must install the extra feature "cli" (or "all") to use the CLI entrypoint.
