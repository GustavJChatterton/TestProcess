import os
from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from GetKmdAcessToken import GetKMDToken
from GetFilarkivAcessToken import GetFilarkivToken
import GetDocumentList
import requests
from requests_ntlm import HttpNtlmAuth
import GenerateCaseFolder
import PrepareEachDocumentToUpload
from email.message import EmailMessage
from getpass import getpass
import smtplib
from io import BytesIO
from SendSMTPMail import send_email, EmailAttachment  # Import the function and dataclass

#   ---- Henter Assets ----
orchestrator_connection = OrchestratorConnection("Henter Assets", os.getenv('OpenOrchestratorSQL'),os.getenv('OpenOrchestratorKey'), None)
GraphAppIDAndTenant = orchestrator_connection.get_credential("GraphAppIDAndTenant")
SharePointAppID = GraphAppIDAndTenant.username
SharePointTenant = GraphAppIDAndTenant.password
SharePointURL = orchestrator_connection.get_constant("AktbobSharePointURL").value
CloudConvert = orchestrator_connection.get_credential("CloudConvertAPI")
CloudConvertAPI = CloudConvert.password
UdviklerMailAktbob =  orchestrator_connection.get_constant("UdviklerMailAktbob").value
RobotCredentials = orchestrator_connection.get_credential("RobotCredentials")
RobotUserName = RobotCredentials.username
RobotPassword = RobotCredentials.password
GOAPILIVECRED = orchestrator_connection.get_credential("GOAktApiUser")
GoUsername = GOAPILIVECRED.username
GoPassword = GOAPILIVECRED.password
KMDNovaURL = orchestrator_connection.get_constant("KMDNovaURL").value
FilarkivURL = orchestrator_connection.get_constant("FilarkivURL").value

# ---- Henter access tokens ----
KMD_access_token = GetKMDToken(orchestrator_connection)
Filarkiv_access_token = GetFilarkivToken(orchestrator_connection)


# ---- Deffinerer Go-session ----
def GO_Session(GoUsername, GoPassword):
    session = requests.Session()
    session.auth = HttpNtlmAuth(GoUsername, GoPassword)
    session.headers.update({
        "Content-Type": "application/json"
    })
    return session

# ---- Initialize Go-Session ----
go_session = GO_Session(GoUsername, GoPassword)


# ---- Henter kø-elementer ----
Sagsnummer = "GEO-2024-043144"
MailModtager = "Gujc@aarhus.dk"
DeskProID = "2088"
DeskProTitel = "Aktindsigt i aktindsigter"
PodioID = "2931863091"
Overmappe = "2088 - Aktindsigt i aktindsigter"
Undermappe = "GEO-2024-043144 - GustavTestAktIndsigt2"
GeoSag = True
NovaSag = False



# ---- Run "GetDokumentlist" ----
Arguments = {
    "in_RobotUserName": RobotUserName,
    "in_RobotPassword": RobotPassword,
    "in_Sagsnummer": Sagsnummer,
    "in_SharePointUrl": SharePointURL,
    "in_Overmappe": Overmappe,
    "in_Undermappe": Undermappe,
    "in_GeoSag": GeoSag, 
    "in_NovaSag": NovaSag,
    "GoUsername": GoUsername,
    "GoPassword":  GoPassword,
    "KMD_access_token": KMD_access_token,
    "KMDNovaURL": KMDNovaURL
}

GetDocumentList_Output_arguments = GetDocumentList.invoke(Arguments, go_session)
Sagstitel = GetDocumentList_Output_arguments.get("sagstitel")
print("Sagstitel:", Sagstitel)
dt_DocumentList = GetDocumentList_Output_arguments.get("dt_DocumentList")



# ---- Run "GenerateCaseFolder" ----
Arguments_GenerateCaseFolder = {
    "in_Sagsnummer": Sagsnummer,
    "in_RobotUserName": RobotUserName,
    "in_RobotPassword": RobotPassword,
    "in_SharePointAppID": SharePointAppID,
    "in_SharePointTenant":SharePointTenant,
    "in_SharePointUrl": SharePointURL,
    "in_Overmappe": Overmappe,
    "in_Undermappe": Undermappe,
    "in_DeskProTitel": DeskProTitel,
    "in_DeskProID": DeskProID,
    "in_Filarkiv_access_token": Filarkiv_access_token,
    "in_Sagstitel": Sagstitel,
    "in_FilarkivURL": FilarkivURL
}

GenerateCaseFolder_Output_arguments = GenerateCaseFolder.invoke_GenerateCasefolder(Arguments_GenerateCaseFolder)
FilarkivCaseID = GenerateCaseFolder_Output_arguments.get("out_FilarkivCaseID")
print(f"FilarkivCaseID: {FilarkivCaseID}")

# ---- Send mail til sagsansvarlig ----
if __name__ == "__main__":
    # Define email details
    sender = "Aktbob<rpamtm001@aarhus.dk>" # Replace with actual sender
    subject = f"Robotten er gået i gang med aktindsigt for {Sagsnummer}"
    body = """Robotten er nu gået i gang med din aktindsigt, og du vil modtage en mail, når den er færdig.<br><br>
    Processen tager typisk et par minutter, men den kan nogle gange være undervejs i flere timer alt efter antallet af dokumenter, 
    der gives aktindsigt til i dokumentlisten og hastigheden på GetOrganized's API.<br><br>
    Det anbefales at følge <a href="https://aarhuskommune.sharepoint.com/:w:/t/tea-teamsite10506/EVjuZhmtsHRGi6H7-COs26AB6afOXvReKSnWJ1XK1mKxZw?e=n03h0t/">vejledningen</a>, 
    hvor du også finder svar på de fleste spørgsmål og fejltyper.<br><br>
    Med venlig hilsen<br><br>
    Teknik & Miljø<br><br>
    Digitalisering<br><br>
    Aarhus Kommune
    """
    smtp_server = "smtp.adm.aarhuskommune.dk"   # Replace with your SMTP server
    smtp_port = 25                    # Replace with your SMTP port

    # Call the send_email function
    send_email(
        receiver=UdviklerMailAktbob,
        sender=sender,
        subject=subject,
        body=body,
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        html_body=True
    )


# ---- Run "PrepareEachDocumentToUpload" ----
Arguments_PrepareEachDocumentToUpload = {
    "in_dt_Documentlist": dt_DocumentList,
    "in_CloudConvertAPI": CloudConvertAPI,
    "in_MailModtager": MailModtager,
    "in_UdviklerMail": UdviklerMailAktbob,
    "in_RobotUserName": RobotUserName,
    "in_RobotPassword": RobotPassword,
    "in_Filarkiv_access_token": Filarkiv_access_token,
    "in_FilarkivCaseID": FilarkivCaseID,
    "in_SharePointAppID": SharePointAppID,
    "in_SharePointTenant":SharePointTenant,
    "in_SharePointUrl": SharePointURL,
    "in_Overmappe": Overmappe,
    "in_Undermappe": Undermappe,
    "in_Sagsnummer": Sagsnummer,
    "in_GeoSag": GeoSag,
    "in_NovaSag": NovaSag,
    "in_FilarkivURL": FilarkivURL,
    "in_NovaToken": KMD_access_token,
    "in_KMDNovaURL": KMDNovaURL,
    "in_GoUsername": GoUsername,
    "in_GoPassword":  GoPassword
}

PrepareEachDocumentToUpload_Output_arguments = PrepareEachDocumentToUpload.invoke_PrepareEachDocumentToUpload(Arguments_PrepareEachDocumentToUpload)
FilarkivCaseID = PrepareEachDocumentToUpload_Output_arguments.get("out_AktIndexDT")
print(f"FilarkivCaseID: {FilarkivCaseID}")




# ---- Run "GenererSagsoversigt" ----


# ---- Run "SendFilarkivCaseId&PodioIDToPodio"