const assert = require('node:assert/strict');
const test = require('node:test');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../installer/vscode-startup/extension.js'), 'utf8');

async function simulate({language = 'python', exists = true, missingApi = false,
    platform = 'linux', managed = true, empty = false, documents = [], tabs = [],
    workspaceFile, remoteName, pointer = '/home/ManSci Code', directory = true, openFails = false} = {}) {
    const calls = {python: [], kernel: [], warnings: [], writes: [], open: []};
    const notebook = {notebookType: 'jupyter-notebook', metadata: {language_info: {name: language}},
        uri: {scheme: 'file', toString: () => 'file:///home/test.ipynb'}, isClosed: false};
    const editor = {notebook};
    const vscode = {
        StatusBarAlignment: {Left: 1},
        env: {remoteName},
        Uri: {file: value => value},
        commands: {executeCommand: async (...args) => {calls.open.push(args); if (openFails) throw Error('Open failed');}},
        window: {
            activeNotebookEditor: empty ? undefined : editor,
            tabGroups: {all: [{tabs}]},
            createOutputChannel: () => ({appendLine() {}, dispose() {}}),
            createStatusBarItem: () => ({show() {}, hide() {}, dispose() {}}),
            showWarningMessage: message => calls.warnings.push(message),
            onDidChangeActiveNotebookEditor: callback => {calls.listener = callback; return {dispose() {}};}
        },
        workspace: {workspaceFolders: empty ? undefined : [{uri: 'home'}], workspaceFile,
            textDocuments: documents, getWorkspaceFolder: () => ({uri: 'home'})},
        extensions: {getExtension: id => ({activate: async () => id === 'ms-python.python' ? {
            environments: {
                updateActiveEnvironmentPath: async (...args) => calls.python.push(args),
                resolveEnvironment: async () => ({id: 'teaching-env', path: '/home/env/python'})
            }
        } : missingApi ? {} : {openNotebook: async (...args) => calls.kernel.push(args)}})}
    };
    const box = {module: {exports: {}}, require: name => name === 'vscode' ? vscode : name === 'path' ? path : {
        existsSync: value => value === '/home/pointer' ? pointer !== null : exists,
        readFileSync: () => pointer, statSync: () => ({isDirectory: () => directory})},
        process: {platform, env: {MANSCI_PYTHON: '/home/env/python', MANSCI_REOPEN_HOME: managed ? '1' : '0',
            MANSCI_WORKSPACE: '/home/default', MANSCI_HOME_POINTER: '/home/pointer'}}, setTimeout};
    vm.runInNewContext(source, box);
    await box.module.exports.activate({subscriptions: []});
    return {calls, editor};
}
test('explicit interpreter and live notebook controller selected once', async () => {
    const {calls, editor} = await simulate();
    assert.equal(calls.python[0][0], '/home/env/python');
    assert.equal(calls.kernel[0][1].id, 'teaching-env');
    await calls.listener(editor);
    assert.equal(calls.kernel.length, 1);
    assert.equal(calls.warnings.length, 0);
});
test('non-Python notebook not changed', async () => {
    const {calls} = await simulate({language: 'julia'});
    assert.equal(calls.kernel.length, 0);
});
test('missing Python reports repair rather than claiming success', async () => {
    const {calls} = await simulate({exists: false});
    assert.equal(calls.kernel.length, 0);
    assert.equal(calls.warnings.length, 1);
});
test('unsupported Jupyter API gives explicit fallback', async () => {
    const {calls} = await simulate({missingApi: true});
    assert.equal(calls.kernel.length, 0);
    assert.equal(calls.warnings.length, 1);
});
test('empty managed Mac Dock window reopens current shared folder once', async () => {
    const {calls} = await simulate({platform: 'darwin', empty: true, pointer: '/home/Changed folder\n'});
    assert.equal(calls.open.length, 1);
    assert.equal(calls.open[0][0], 'vscode.openFolder');
    assert.equal(calls.open[0][1], '/home/Changed folder');
    assert.equal(calls.open[0][2].forceReuseWindow, true);
    assert.equal(calls.python.length, 0);
});
test('missing pointer falls back to the launch folder', async () => {
    const {calls} = await simulate({platform: 'darwin', empty: true, pointer: null});
    assert.equal(calls.open[0][1], '/home/default');
});
test('does not replace explicit workspaces, files, unsaved tabs or remote windows', async () => {
    for (const extra of [{empty: false}, {workspaceFile: 'chosen.code-workspace'},
        {documents: [{isUntitled: true}]}, {documents: [{uri: {scheme: 'file'}}]},
        {tabs: [{}]}, {remoteName: 'ssh-remote'}]) {
        const {calls} = await simulate({platform: 'darwin', empty: true, ...extra});
        assert.equal(calls.open.length, 0);
    }
});
test('does not redirect Windows or an ordinary Mac process', async () => {
    for (const extra of [{platform: 'win32'}, {platform: 'darwin', managed: false}]) {
        const {calls} = await simulate({empty: true, ...extra});
        assert.equal(calls.open.length, 0);
    }
});
test('invalid home and failed open warn without retry loops', async () => {
    for (const extra of [{pointer: 'relative/path'}, {directory: false}, {openFails: true}]) {
        const {calls} = await simulate({platform: 'darwin', empty: true, ...extra});
        assert.equal(calls.warnings.length, 1);
        assert.ok(calls.open.length <= 1);
    }
});
