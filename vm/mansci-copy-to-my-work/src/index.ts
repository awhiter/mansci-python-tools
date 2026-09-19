import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { Dialog, InputDialog, showDialog, ToolbarButton } from '@jupyterlab/apputils';
import { PageConfig, URLExt } from '@jupyterlab/coreutils';
import { IFileBrowserFactory } from '@jupyterlab/filebrowser';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { ServerConnection } from '@jupyterlab/services';

import '../style/index.css';

const COPY_COMMAND = 'mansci:copy-to-my-work';
const TEAM_COMMAND = 'mansci:team-exchange';
const SHARE_COMMAND = 'mansci:copy-to-team-exchange';
const TEACHING_PREFIX = 'Teaching Materials/';
const TEAM_PREFIX = 'Team Exchange/';

function correctFutureTimestampLabel(): void {
  document.querySelectorAll('.jp-DirListing-itemModified').forEach(node => {
    if (node.textContent?.trim() === 'next yr.') {
      node.textContent = 'now';
    }
  });
}

interface TeamInfo {
  name: string;
  join_code: string;
  members: string[];
  member_count: number;
  maximum_members: number;
}

interface TeamStatus {
  role: 'student' | 'staff';
  maximum_members: number;
  team?: TeamInfo | null;
  teams?: TeamInfo[];
}

function isModuleLead(): boolean {
  const match = PageConfig.getBaseUrl().match(/\/user\/([^/]+)\//);
  return !!match && decodeURIComponent(match[1]).endsWith('_lead');
}

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

async function teamRequest(payload?: object): Promise<any> {
  const settings = ServerConnection.makeSettings();
  const url = URLExt.join(PageConfig.getBaseUrl(), 'mansci-team-exchange');
  const response = await ServerConnection.makeRequest(
    url,
    payload
      ? { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }
      : {},
    settings
  );
  const result = await response.json();
  if (!response.ok) {
    throw new ServerConnection.ResponseError(response, result.reason || result.message || 'Team Exchange request failed');
  }
  return result;
}

function teamSummary(team: TeamInfo): string {
  return `${team.name}\n\nJoin code: ${team.join_code}\nStudents: ${team.members.join(', ') || 'none'}\nPlaces: ${team.member_count}/${team.maximum_members}`;
}

async function manageTeamExchange(browserFactory: IFileBrowserFactory): Promise<void> {
  try {
    const status = await teamRequest() as TeamStatus;
    if (status.role === 'staff') {
      const teams = status.teams || [];
      await message(
        'Team Exchange — staff view',
        teams.length
          ? teams.map(team => teamSummary(team)).join('\n\n———\n\n')
          : 'No student teams have been created yet.'
      );
      return;
    }
    if (status.team) {
      const result = await showDialog({
        title: `Team Exchange — ${status.team.name}`,
        body: teamSummary(status.team),
        buttons: [Dialog.cancelButton({ label: 'Close' }), Dialog.warnButton({ label: 'Leave team' })]
      });
      if (result.button.label === 'Leave team') {
        const confirm = await showDialog({
          title: `Leave ${status.team.name}?`,
          body: 'You will lose access to this Team Exchange. Files you already shared will remain with the team.',
          buttons: [Dialog.cancelButton(), Dialog.warnButton({ label: 'Leave team' })]
        });
        if (confirm.button.label === 'Leave team') {
          const left = await teamRequest({ action: 'leave' });
          await browserFactory.tracker.currentWidget?.model.refresh();
          await message('Team Exchange', left.message);
        }
      }
      return;
    }
    const decision = await showDialog({
      title: 'Team Exchange',
      body: `Create a named team or join one using its code. Teams can contain up to ${status.maximum_members} students.`,
      buttons: [
        Dialog.cancelButton(),
        Dialog.createButton({ label: 'Join a team' }),
        Dialog.createButton({ label: 'Create a team' })
      ]
    });
    if (decision.button.label === 'Create a team') {
      const entered = await InputDialog.getText({
        title: 'Name your team',
        label: 'Team name',
        placeholder: 'For example: Decision Dynamics'
      });
      if (entered.button.accept && entered.value) {
        const created = await teamRequest({ action: 'create', name: entered.value });
        await browserFactory.tracker.currentWidget?.model.refresh();
        await message(`Team Exchange — ${created.team.name}`, teamSummary(created.team));
      }
    } else if (decision.button.label === 'Join a team') {
      const entered = await InputDialog.getText({
        title: 'Join a Team Exchange',
        label: 'Join code',
        placeholder: 'For example: MAPLE-47'
      });
      if (entered.button.accept && entered.value) {
        const joined = await teamRequest({ action: 'join', code: entered.value });
        await browserFactory.tracker.currentWidget?.model.refresh();
        await message(`Joined ${joined.team.name}`, teamSummary(joined.team));
      }
    }
  } catch (error) {
    await message('Team Exchange', error instanceof Error ? error.message : String(error));
  }
}

async function prepareEditableCopy(panel: NotebookPanel): Promise<void> {
  const sessionContext = panel.sessionContext as any;
  sessionContext.kernelPreference = {
    ...(sessionContext.kernelPreference || {}),
    canStart: true,
    shouldStart: true,
    autoStartDefault: true
  };
  await panel.context.ready;
  if (panel.content.model) {
    panel.content.model.readOnly = false;
  }
  await sessionContext.ready;
  if (sessionContext.hasNoKernel) {
    await sessionContext.startKernel();
  }
  if (sessionContext.session?.kernel) {
    await sessionContext.session.kernel.info;
  }
}

async function protectTeachingNotebook(
  app: JupyterFrontEnd,
  panel: NotebookPanel
): Promise<void> {
  const teaching = panel.context.path.startsWith(TEACHING_PREFIX);
  const teamExchange = panel.context.path.startsWith(TEAM_PREFIX);
  if (!teaching && !teamExchange) {
    return;
  }
  // Module leads own and maintain the centrally managed source material.
  // The view-only workflow applies to student accounts only.
  if (teaching && isModuleLead()) {
    return;
  }

  // Apply this before waiting for the document model. Otherwise JupyterLab can
  // begin its normal kernel-selection flow while the protected file opens.
  const sessionContext = panel.sessionContext as any;
  sessionContext.kernelPreference = {
    ...(sessionContext.kernelPreference || {}),
    canStart: false,
    shouldStart: false,
    autoStartDefault: false
  };

  await panel.context.ready;

  if (panel.content.model) {
    panel.content.model.readOnly = true;
  }
  panel.node.classList.add('mansci-teaching-readonly');
  panel.title.caption = teamExchange
    ? 'Team Exchange snapshot — use Copy to My Work before editing or running'
    : 'View-only Teaching Material — use Copy to My Work before editing or running';

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
        const copied = await app.commands.execute('docmanager:open', {
          path: destination
        });
        if (copied instanceof NotebookPanel) {
          await prepareEditableCopy(copied);
        }
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
    // JupyterLab 4.6 renders a tiny positive server/browser clock difference
    // as "next yr.". Correct only that known file-browser label.
    const timestampObserver = new MutationObserver(correctFutureTimestampLabel);
    timestampObserver.observe(document.body, {
      childList: true,
      subtree: true,
      characterData: true
    });
    correctFutureTimestampLabel();
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
    app.commands.addCommand(TEAM_COMMAND, {
      label: 'Team Exchange: Create, Join or View Team',
      execute: () => manageTeamExchange(browserFactory)
    });
    app.contextMenu.addItem({
      command: TEAM_COMMAND,
      selector: '.jp-DirListing-content',
      rank: 5.1
    });
    app.commands.addCommand(SHARE_COMMAND, {
      label: 'Copy to Team Exchange',
      isEnabled: () => {
        const browser = browserFactory.tracker.currentWidget;
        if (!browser) {
          return false;
        }
        const selected = Array.from(browser.selectedItems());
        return selected.length === 1 &&
          !selected[0].path.startsWith('Teaching Materials/') &&
          selected[0].path !== 'Teaching Materials';
      },
      execute: async () => {
        const browser = browserFactory.tracker.currentWidget;
        if (!browser) {
          return;
        }
        const selected = Array.from(browser.selectedItems());
        if (selected.length !== 1) {
          return message('Team Exchange', 'Select one file or folder in your workspace.');
        }
        try {
          const status = await teamRequest() as TeamStatus;
          if (!status.team) {
            return message('Team Exchange', 'Create or join a team before sharing work.');
          }
          const result = await teamRequest({
            action: 'share', source: selected[0].path
          });
          await browser.model.refresh();
          await message(`Team Exchange — ${status.team.name}`, result.message);
        } catch (error) {
          await message('Team Exchange', error instanceof Error ? error.message : String(error));
        }
      }
    });
    app.contextMenu.addItem({
      command: SHARE_COMMAND,
      selector: '.jp-DirListing-item',
      rank: 5.05
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
