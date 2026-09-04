const assert = require('node:assert/strict');
const test = require('node:test');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../installer/vscode-startup/extension.js'), 'utf8');

async function simulate({language = 'python', exists = true, missingApi = false} = {}) {
    const calls = {python: [], kernel: [], warnings: [], writes: []};
    const notebook = {notebookType: 'jupyter-notebook', metadata: {language_info: {name: language}},
        uri: {scheme: 'file', toString: () => 'file:///home/test.ipynb'}, isClosed: false};
    const editor = {notebook};
    const vscode = {
        StatusBarAlignment: {Left: 1},
        window: {
            activeNotebookEditor: editor,
            createOutputChannel: () => ({appendLine() {}, dispose() {}}),
            createStatusBarItem: () => ({show() {}, hide() {}, dispose() {}}),
            showWarningMessage: message => calls.warnings.push(message),
            onDidChangeActiveNotebookEditor: callback => {calls.listener = callback; return {dispose() {}};}
        },
        workspace: {workspaceFolders: [{uri: 'home'}], getWorkspaceFolder: () => ({uri: 'home'})},
        extensions: {getExtension: id => ({activate: async () => id === 'ms-python.python' ? {
            environments: {
                updateActiveEnvironmentPath: async (...args) => calls.python.push(args),
                resolveEnvironment: async () => ({id: 'teaching-env', path: '/home/env/python'})
            }
        } : missingApi ? {} : {openNotebook: async (...args) => calls.kernel.push(args)}})}
    };
    const box = {module: {exports: {}}, require: name => name === 'vscode' ? vscode : {existsSync: () => exists},
        process: {env: {MANSCI_PYTHON: '/home/env/python'}}, setTimeout};
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
