import { createRoot } from 'react-dom/client';
import PropertiesView from './PropertiesView';

/**
 * @note The base of this component is heavily inspired from 
 * https://github.com/bpmn-io/bpmn-js-example-react-properties-panel
 */
export default class PropertiesPanel {
  constructor(options: { modeler: any; container: HTMLElement }) {
    const { modeler, container } = options;

    // @ts-ignore
    if (!container._reactRoot) {
      // @ts-ignore
      container._reactRoot = createRoot(container);
    }
    // @ts-ignore
    container._reactRoot.render(<PropertiesView modeler={modeler} />);
  }
}
