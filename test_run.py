from cutlist_calculator import calculate_drawer, calculate_toolbox_frame

# basic smoke test values
try:
    result = calculate_drawer(
        drwL=400.0, drwW=300.0,
        drwHt=50.0, drwHm=50.0, drwHb=50.0,
        tBox=15.0, sDado=6.0,
        cBox=25.0, cBase=15.0
    )
    frame = calculate_toolbox_frame(
        drawers=result,
        tSlides=12.0,
        sRear=40.0,
        sFront=5.0,
        nDrwT=1, nDrwM=1, nDrwB=1, nDrw=3,
        sDrw=2.0,
        tBkt=2.0
    )
    print('SMOKE_TEST: OK')
    print('drawer keys:', sorted(result.keys()))
    print('frame keys:', sorted(frame.keys()))
except Exception as e:
    print('SMOKE_TEST: FAIL')
    raise
