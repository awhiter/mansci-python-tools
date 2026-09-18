import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { Dialog, showDialog, ToolbarButton } from '@jupyterlab/apputils';
import { PageConfig, URLExt } from '@jupyterlab/coreutils';
import { IFileBrowserFactory } from '@jupyterlab/filebrowser';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { ServerConnection } from '@jupyterlab/services';

import '../style/index.css';

const COPY_COMMAND = 'mansci:copy-to-my-work';
const TEACHING_PREFIX = 'Teaching Materials/';

async function message(title: string, body: string): Promise<void> {
  await showDialog({ title, body, buttons: [Dialog.okButton()] });
}

async function copyPath(source: string): Promise<string> {
  const settings = ServerConnection.makeSettings();
  const url = URLExt.join(PageConfig.getBaseUrl(), 'mansci-copy-to-my-work');
  const response = await ServerConnection.makeRequest(
    url,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source })
    },
    settings
  );
  const result = await response.json();
  if (!response.ok) {
    throw new ServerConnection.ResponseError(
      response,
      result.reason || result.message || 'Copy failed'
    );
  }
  return result.destination as string;
}

async function protectTeachingNotebook(
  app: JupyterFrontEnd,
  panel: NotebookPanel
): Promise<void> {
  await panel.context.ready;
  if (!panel.context.path.startsWith(TEACHING_PREFIX)) {
    return;
  }

  if (panel.content.model) {
    panel.content.model.readOnly = true;
  }
  panel.node.classList.add('mansci-teaching-readonly');
  panel.title.caption =
    'View-only Teaching Material — use Copy to My Work before editing or running';

  const sessionContext = panel.sessionContext as any;
  sessionContext.kernelPreference = {
    ...(sessionContext.kernelPreference || {}),
    canStart: false,
    shouldStart: false,
    autoStartDefault: false
  };
  await sessionContext.ready;
  if (sessionContext.session) {
    await sessionContext.shutdown();
  }

  const copyButton = new ToolbarButton({
    label: 'Copy to My Work',
    tooltip: 'Create an editable copy in My Work',
    onClick: async () => {
      try {
        const destination = await copyPath(panel.context.path);
        await app.commands.execute('docmanager:open', { path: destination });
      } catch (error) {
        await message(
          'Copy to My Work',
          error instanceof Error ? error.message : String(error)
        );
      }
    }
  });
  copyButton.addClass('mansci-copy-open-button');
  panel.toolbar.insertItem(0, 'mansci-copy-to-my-work', copyButton);
}

const plugin: JupyterFrontEndPlugin<void> = {
  id: '@mansci/copy-to-my-work:plugin',
  description:
    'Copy teaching materials into My Work and keep centrally managed notebooks view-only.',
  autoStart: true,
  requires: [IFileBrowserFactory, INotebookTracker],
  activate: (
    app: JupyterFrontEnd,
    browserFactory: IFileBrowserFactory,
    notebooks: INotebookTracker
  ) => {
    app.commands.addCommand(COPY_COMMAND, {
      label: 'Copy to My Work',
      isEnabled: () => {
        const browser = browserFactory.tracker.currentWidget;
        return !!browser && Array.from(browser.selectedItems()).length === 1;
      },
      execute: async () => {
        const browser = browserFactory.tracker.currentWidget;
        if (!browser) {
          return message('Copy to My Work', 'The file browser is not available.');
        }
        const selected = Array.from(browser.selectedItems());
        if (selected.length !== 1) {
          return message('Copy to My Work', 'Please select one file or folder.');
        }
        try {
          const destination = await copyPath(selected[0].path);
          await browser.model.refresh();
          await message('Copied to My Work', `Copied to ${destination}.`);
        } catch (error) {
          await message(
            'Copy to My Work',
            error instanceof Error ? error.message : String(error)
          );
        }
      }
    });
    app.contextMenu.addItem({
      command: COPY_COMMAND,
      selector: '.jp-DirListing-item',
      rank: 5
    });
    notebooks.widgetAdded.connect((_sender, panel) => {
      void protectTeachingNotebook(app, panel);
    });
    notebooks.forEach(panel => {
      void protectTeachingNotebook(app, panel);
    });
  }
};

export default plugin;
