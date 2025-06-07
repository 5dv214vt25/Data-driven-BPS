import BpmnDiagram from '../BpmnDiagram';

export default function BpmnTab() {
  return (
    <div>
      <BpmnDiagram bpmnXml={''} jsonData={{}} setJsonData={() => { }} showSidePanel={true} />
      <p>Simconfig</p>
    </div>
  );
}

