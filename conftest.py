from armicontrib.dif3d.tests import dif3dTestingApp


def pytest_sessionstart(session):
    import armi

    if not armi.isConfigured():
        armi.configure(dif3dTestingApp.Dif3dTestingApp())
