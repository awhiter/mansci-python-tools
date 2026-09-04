// Local-only helper. Never executes notebook cells or edits notebook files.
// Jupyter openNotebook is an exported but unstable API: the distribution pins
// Jupyter and checks this capability. Fail visibly rather than guess kernel IDs.
const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

async function reopenMacHome(output) {
    // Only the isolated Mac process launched by ManSci opts into this behaviour.
    // Preserve remote windows, explicit workspaces, loose files and unsaved tabs.
    if (process.platform !== 'darwin' || process.env.MANSCI_REOPEN_HOME !== '1' ||
        vscode.env.remoteName || vscode.workspace.workspaceFile ||
        vscode.workspace.workspaceFolders?.length ||
        vscode.workspace.textDocuments?.some(doc => !doc.isClosed && (doc.isUntitled || doc.uri.scheme === 'file')) ||
        vscode.window.tabGroups?.all.some(group => group.tabs.length)) return false;
    try {
        let home = process.env.MANSCI_WORKSPACE;
        const pointer = process.env.MANSCI_HOME_POINTER;
        if (pointer && fs.existsSync(pointer)) home = fs.readFileSync(pointer, 'utf8').trim();
        if (!home || !path.isAbsolute(home) || !fs.statSync(home).isDirectory()) {
            throw Error('The shared coding folder is missing or its path is invalid.');
        }
        output.appendLine('Reopening shared coding folder: ' + home);
        await vscode.commands.executeCommand('vscode.openFolder', vscode.Uri.file(home), {forceReuseWindow: true});
        return true;
    } catch (error) {
        output.appendLine('Could not reopen ManSci home: ' + String(error));
        vscode.window.showWarningMessage('ManSci could not reopen the shared coding folder. Use File → Open Folder or check Documents/ManSci Code Home.txt.');
        return false;
    }
}

async function activate(context) {
    const output = vscode.window.createOutputChannel('ManSci Startup');
    const status = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 1);
    context.subscriptions.push(output, status);
    if (await reopenMacHome(output)) return;
    const python = process.env.MANSCI_PYTHON;
    if (!python || !fs.existsSync(python)) {
        output.appendLine('Installed Python path is missing. Rerun the ManSci installer.');
        vscode.window.showWarningMessage('ManSci Python is missing. Close VS Code and rerun the ManSci installer.');
        return;
    }
    status.text = '$(sync~spin) Preparing ManSci Python';
    status.show();
    let py;
    try {
        py = await vscode.extensions.getExtension('ms-python.python').activate();
        if (py.ready) await py.ready;
        for (const folder of vscode.workspace.workspaceFolders || []) {
            await py.environments.updateActiveEnvironmentPath(python, folder.uri);
        }
        output.appendLine('Python selected: ' + python);
    } catch (error) {
        output.appendLine(String(error));
        status.text = '$(warning) ManSci Python setup failed';
        return;
    }
    status.hide();
    const selected = new WeakSet();
    const pending = new WeakSet();
    async function prepare(editor) {
        if (!editor) return;
        const notebook = editor.notebook;
        if (notebook.notebookType !== 'jupyter-notebook' || selected.has(notebook) || pending.has(notebook)) return;
        const language = notebook.metadata.language_info?.name || notebook.metadata.kernelspec?.language || 'python';
        if (language.toLowerCase() !== 'python') return;
        if (notebook.uri.scheme !== 'untitled' && !vscode.workspace.getWorkspaceFolder(notebook.uri)) return;
        pending.add(notebook);
        status.text = '$(sync~spin) Preparing ManSci kernel';
        status.show();
        let failure;
        try {
            const jupyter = await vscode.extensions.getExtension('ms-toolsai.jupyter').activate();
            if (jupyter.ready) await jupyter.ready;
            if (typeof jupyter.openNotebook !== 'function') throw Error('Installed Jupyter version does not support managed kernel selection.');
            for (let attempt = 0; attempt < 5; attempt++) {
                if (notebook.isClosed || vscode.window.activeNotebookEditor !== editor) return;
                try {
                    const environment = await py.environments.resolveEnvironment(python);
                    if (!environment) throw Error('Teaching environment discovery is still in progress.');
                    if (notebook.isClosed || vscode.window.activeNotebookEditor !== editor) return;
                    // This explicitly selects the controller; metadata alone did not.
                    await jupyter.openNotebook(notebook.uri, {id: environment.id, path: environment.path});
                    selected.add(notebook);
                    output.appendLine('Kernel selected: ' + notebook.uri.toString());
                    return;
                } catch (error) {
                    failure = error;
                    if (attempt < 4) await new Promise(resolve => setTimeout(resolve, 1000 * 2 ** attempt));
                }
            }
            throw failure;
        } catch (error) {
            output.appendLine('Kernel selection failed: ' + String(error));
            vscode.window.showWarningMessage('ManSci could not automatically select this notebook kernel. Choose Management Science Python, then send staff the ManSci Startup output.');
        } finally {
            pending.delete(notebook);
            status.hide();
        }
    }
    context.subscriptions.push(vscode.window.onDidChangeActiveNotebookEditor(prepare));
    await prepare(vscode.window.activeNotebookEditor);
}
module.exports = {activate};
