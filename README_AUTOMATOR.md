# Setting Up MergePDF as a Finder Quick Action

This guide will help you set up a macOS Quick Action (formerly known as a Service) that allows you to merge two PDF files directly from Finder. The Quick Action will appear in the context menu when you right-click on PDF files.

## Prerequisites

Before setting up the Quick Action, ensure:

1. You have successfully installed and tested the MergePDF application
2. The FastAPI service is running (check with `curl http://localhost:8000/api/health`)
3. You have tested the CLI script (`merge_pdfs_cli.sh`) and Automator handler (`automator_handler.sh`)

## Creating the Automator Quick Action

### Step 1: Open Automator

Open the Automator application from your Applications folder or using Spotlight (Cmd+Space, then type "Automator").

![Open Automator - Screenshot placeholder]

### Step 2: Create a New Quick Action

1. When Automator opens, select "Quick Action" (or "Service" in older macOS versions) from the document type chooser.
2. Click "Choose" to create a new workflow.

![Create New Quick Action - Screenshot placeholder]

### Step 3: Configure the Workflow Settings

In the workflow configuration at the top of the window:

1. Set "Workflow receives" to **files or folders**
2. Set "in" to **Finder**
3. Choose an appropriate icon (optional, the PDF icon is recommended)
4. Set the color as desired (optional)

![Configure Workflow Settings - Screenshot placeholder]

### Step 4: Add a Filter Action

1. Search for "Filter Finder Items" in the actions library (left sidebar) and drag it to the workflow area
2. Configure the filter to only accept PDF files:
   - Set "All" criteria must be met
   - Add a condition: "Kind is PDF document"

![Add Filter Action - Screenshot placeholder]

### Step 5: Add a Run Shell Script Action

1. Search for "Run Shell Script" in the actions library and drag it below the filter action
2. Configure the shell script action:
   - Shell: `/bin/bash`
   - Pass input: **as arguments**
   - Replace the default script with the following code:

```bash
# Path to the MergePDF directory
MERGEPDF_DIR="/Users/yannrapaport/Documents/Dev/mergepdf"
cd "$MERGEPDF_DIR"

# Check if we have exactly 2 files
if [ $# -ne 2 ]; then
    osascript -e 'display dialog "Please select exactly two PDF files." buttons {"OK"} default button "OK" with icon stop with title "MergePDF Error"'
    exit 1
fi

# Run the Automator handler script
"$MERGEPDF_DIR/automator_handler.sh" "$1" "$2"
```

**Important**: Update the `MERGEPDF_DIR` path to match your actual installation directory.

![Add Run Shell Script Action - Screenshot placeholder]

### Step 6: Save the Quick Action

1. Click File > Save or press Cmd+S
2. Name your workflow "Merge PDFs (Odd/Even)"
3. Click Save

The workflow will be saved to `~/Library/Services/Merge PDFs (Odd/Even).workflow`.

![Save Quick Action - Screenshot placeholder]

## Testing the Quick Action

To test your new Quick Action:

1. Navigate to a folder containing two PDF files (such as scan files)
2. Select exactly two PDF files in Finder
3. Right-click on the selected files
4. Go to "Quick Actions" in the context menu (or "Services" in older macOS)
5. Select "Merge PDFs (Odd/Even)"
6. Follow the on-screen prompts to specify which file contains odd pages
7. The merged PDF should automatically open when complete

## Configuration Details

### Service Locations

- Automator workflow: `~/Library/Services/Merge PDFs (Odd/Even).workflow`
- API service: Configured via launchd in `~/Library/LaunchAgents/com.yannrapaport.mergepdf-api.plist`
- Log files: Located in the `logs` directory of your MergePDF installation

### Permissions

The Quick Action needs permission to:
- Access files in Finder
- Run shell scripts
- Display notifications/dialogs
- Access the network (to communicate with the API)

You may be prompted to grant these permissions when first running the service.

## Troubleshooting

### Quick Action Doesn't Appear in Context Menu

1. Make sure you've selected exactly two PDF files
2. Try restarting the Finder:
   ```
   killall Finder
   ```
3. Check if the workflow was saved correctly:
   ```
   ls -la ~/Library/Services/
   ```

### API Connection Errors

1. Verify the API service is running:
   ```
   curl http://localhost:8000/api/health
   ```
2. Check the API logs for errors:
   ```
   cat /Users/yannrapaport/Documents/Dev/mergepdf/logs/api_*.log
   ```
3. Restart the API service if needed:
   ```
   launchctl unload ~/Library/LaunchAgents/com.yannrapaport.mergepdf-api.plist
   launchctl load ~/Library/LaunchAgents/com.yannrapaport.mergepdf-api.plist
   ```

### Script Execution Errors

1. Check the Automator handler logs:
   ```
   cat /Users/yannrapaport/Documents/Dev/mergepdf/logs/automator.log
   ```
2. Ensure all scripts have execute permissions:
   ```
   chmod +x /Users/yannrapaport/Documents/Dev/mergepdf/*.sh
   ```
3. Test the scripts directly from the terminal

## Customization Options

### Changing the Output Directory

By default, merged PDFs are saved to your Downloads folder. To change this:

1. Edit `merge_pdfs_cli.sh` and modify the `OUTPUT_DIR` variable
2. Or use the `--dir` option when calling the script

### Adding to the Touch Bar

You can add frequently used Quick Actions to the Touch Bar (if your Mac has one):

1. Open System Preferences > Extensions > Touch Bar
2. Add "Merge PDFs (Odd/Even)" to the Touch Bar control strip

### Creating a Keyboard Shortcut

To assign a keyboard shortcut to your Quick Action:

1. Open System Preferences > Keyboard > Shortcuts
2. Select "Services" from the left sidebar
3. Find "Merge PDFs (Odd/Even)" in the list
4. Click on it and assign a keyboard shortcut

## Uninstalling

To remove the Quick Action:

1. Delete the workflow file:
   ```
   rm -rf ~/Library/Services/Merge\ PDFs\ \(Odd/Even\).workflow
   ```
2. Unload the API service:
   ```
   launchctl unload ~/Library/LaunchAgents/com.yannrapaport.mergepdf-api.plist
   ```
3. Remove the launchd configuration:
   ```
   rm ~/Library/LaunchAgents/com.yannrapaport.mergepdf-api.plist
   ```

