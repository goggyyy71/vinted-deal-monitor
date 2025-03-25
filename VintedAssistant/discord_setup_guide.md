# Discord Webhook Setup Guide

1. **Open Your Discord Server**
   - Open Discord and go to the server where you want to receive Vinted deal notifications
   - Make sure you have "Manage Webhooks" permission in the server

2. **Create a Webhook**
   - Right-click on the channel where you want to receive notifications
   - Select "Edit Channel"
   - Click on "Integrations"
   - Click on "Create Webhook"
   - Give your webhook a name (e.g., "Vinted Deals")
   - Optional: Set a custom avatar for the webhook
   - Click "Copy Webhook URL" to get your webhook link

3. **Use the Webhook in Vinted Monitor**
   - Go back to the Vinted Monitor application
   - In the sidebar, paste your webhook URL into the "Discord Webhook URL" field
   - The URL should look something like: `https://discord.com/api/webhooks/...`

4. **Test the Webhook**
   - Start monitoring by clicking the "Toggle Monitoring" button
   - When a deal is found, you should receive a notification in your Discord channel
   - The notification will include:
     - Item title
     - Price
     - Potential profit
     - Direct link to the listing
     - Item image (if available)

**Note**: Keep your webhook URL private and never share it publicly, as it can be used to send messages to your channel.
