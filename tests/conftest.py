import os,pytest,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from conf import base_url_conf
from conf import report_portal_conf
from utils import post_test_reports_to_slack
from utils.email_pytest_report import Email_Pytest_Report
from endpoints.API_Player import API_Player

@pytest.fixture
def test_api_obj(api_url=base_url_conf.api_base_url):
    "Return an instance of Base Page that knows about the third party integrations"
    try:
        test_api_obj = API_Player(url=api_url, session_flag=True)
        yield test_api_obj

    except Exception as e:
        print("Exception when trying to run test:%s" % __file__)
        print("Python says:%s" % str(e))

@pytest.fixture
def email_pytest_report(request):
    "pytest fixture for device flag"
    try:
        return request.config.getoption("--email_pytest_report")

    except Exception as e:
        print("Exception when trying to run test: %s"%__file__)
        print("Python says:%s"%str(e))

@pytest.fixture
def reportportal_service(request):
    "pytest service fixture for reportportal"
    reportportal_pytest_service = None
    try:
       if request.config.getoption("--reportportal"):
           reportportal_pytest_service = request.node.config.py_test_service
    except Exception as e:
        print("Exception when trying to run test: %s"%__file__)
        print("Python says:%s"%str(e))

    return reportportal_pytest_service


@pytest.hookimpl()
def pytest_configure(config):
    "Sets the launch name based on the marker selected."
    global if_reportportal
    if_reportportal =config.getoption('--reportportal')

    try:
        config._inicache["rp_uuid"] = report_portal_conf.report_portal_uuid
        config._inicache["rp_endpoint"]= report_portal_conf.report_portal_endpoint
        config._inicache["rp_project"]=report_portal_conf.report_portal_project
        config._inicache["rp_launch"]=report_portal_conf.report_portal_launch

    except Exception as e:
        print("Exception when trying to run test: %s"%__file__)
        print("Python says:%s"%str(e))

    #Registering custom markers to supress warnings
    config.addinivalue_line("markers", "GUI: mark a test as part of the GUI regression suite.")
    config.addinivalue_line("markers", "API: mark a test as part of the GUI regression suite.")
    config.addinivalue_line("markers", "MOBILE: mark a test as part of the GUI regression suite.")

def pytest_terminal_summary(terminalreporter, exitstatus):
    "add additional section in terminal summary reporting."
    try:
        if not hasattr(terminalreporter.config, 'workerinput'):
            if  terminalreporter.config.getoption("--slack_flag").lower() == 'y':
                post_test_reports_to_slack.post_reports_to_slack()
            if terminalreporter.config.getoption("--email_pytest_report").lower() == 'y':
                #Initialize the Email_Pytest_Report object
                email_obj = Email_Pytest_Report()
                # Send html formatted email body message with pytest report as an attachment
                email_obj.send_test_report_email(html_body_flag=True,attachment_flag=True,report_file_path='default')

    except Exception as e:
        print("Exception when trying to run test: %s"%__file__)
        print("Python says:%s"%str(e))

def pytest_addoption(parser):
    "Method to add the option to ini."
    try:
        parser.addini("rp_uuid",'help',type="pathlist")
        parser.addini("rp_endpoint",'help',type="pathlist")
        parser.addini("rp_project",'help',type="pathlist")
        parser.addini("rp_launch",'help',type="pathlist")

        parser.addoption("--api_url",
                            dest="url",
                            default="https://cars-app.qxf2.com/",
                            help="The url of the api")
        parser.addoption("--slack_flag",
                            dest="slack_flag",
                            default="N",
                            help="Post the test report on slack channel: Y or N")
        parser.addoption("--email_pytest_report",
                            dest="email_pytest_report",
                            help="Email pytest report: Y or N",
                            default="N")
        parser.addoption("--interactive_mode_flag",
                            dest="questionary",
                            default="n",
                            help="set the questionary flag")

    except Exception as e:
        print("Exception when trying to run test: %s"%__file__)
        print("Python says:%s"%str(e))
