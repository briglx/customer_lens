"""Wrapper class for Microsoft Graph API."""
from configparser import SectionProxy

from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.email_address import EmailAddress
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.message import Message
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.users.item.mail_folders.item.messages.messages_request_builder import (
    MessagesRequestBuilder,
)
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import (
    SendMailPostRequestBody,
)
from msgraph.generated.users.item.user_item_request_builder import (
    UserItemRequestBuilder,
)


class Graph:
    """Wrapper class for Microsoft Graph API."""

    settings: SectionProxy
    device_code_credential: DeviceCodeCredential
    user_client: GraphServiceClient

    def __init__(self, config: SectionProxy):
        """Initialize Graph object."""
        self.settings = config
        client_id = self.settings["clientId"]
        tenant_id = self.settings["tenantId"]
        graph_scopes = self.settings["graphUserScopes"].split(" ")

        self.device_code_credential = DeviceCodeCredential(
            client_id, tenant_id=tenant_id
        )
        self.user_client = GraphServiceClient(self.device_code_credential, graph_scopes)

    async def get_user_token(self):
        """Get access token for user."""
        graph_scopes = self.settings["graphUserScopes"]
        access_token = self.device_code_credential.get_token(graph_scopes)
        return access_token.token

    async def get_user(self):
        """Get signed-in user."""
        query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
            select=["displayName", "mail", "userPrincipalName"]
        )

        request_config = (
            UserItemRequestBuilder.UserItemRequestBuilderGetRequestConfiguration(
                query_parameters=query_params
            )
        )

        user = await self.user_client.me.get(request_configuration=request_config)
        return user

    async def get_inbox(self):
        """Get top 25 messages in user's inbox."""
        query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
            # Only request specific properties
            select=["from", "isRead", "receivedDateTime", "subject"],
            # Get at most 25 results
            top=25,
            # Sort by received time, newest first
            orderby=["receivedDateTime DESC"],
        )
        request_config = (
            MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
                query_parameters=query_params
            )
        )

        messages = await self.user_client.me.mail_folders.by_mail_folder_id(
            "inbox"
        ).messages.get(request_configuration=request_config)
        return messages

    async def send_mail(self, subject: str, body: str, recipient: str):
        """Send mail to recipient."""
        message = Message()
        message.subject = subject

        message.body = ItemBody()
        message.body.content_type = BodyType.Text
        message.body.content = body

        to_recipient = Recipient()
        to_recipient.email_address = EmailAddress()
        to_recipient.email_address.address = recipient
        message.to_recipients = []
        message.to_recipients.append(to_recipient)

        request_body = SendMailPostRequestBody()
        request_body.message = message

        await self.user_client.me.send_mail.post(body=request_body)

    async def make_graph_call(self):
        """Make a generic Graph call to endpoint."""
        return
