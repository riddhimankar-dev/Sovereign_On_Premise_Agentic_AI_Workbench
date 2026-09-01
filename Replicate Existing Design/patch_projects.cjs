const fs = require('fs');
const file = 'src/screens/ProjectsScreen.tsx';
let content = fs.readFileSync(file, 'utf8');

const importApi = `import { useState, useEffect } from "react";\nimport { api, Project } from "../services/api";\n`;
content = content.replace('import { FolderOpen', importApi + 'import { FolderOpen');

content = content.replace(/const projects = \[[^]*?\];/, '');

const componentStart = 'export default function ProjectsScreen({ onSelectProject }: { onSelectProject?: () => void }) {';
const newComponentStart = `${componentStart}
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.projects.list().then(res => {
      setProjects(res.projects);
      setLoading(false);
    }).catch(e => {
      console.error(e);
      setLoading(false);
    });
  }, []);
`;
content = content.replace(componentStart, newComponentStart);

// Map project to UI
content = content.replace(/projects\.map\(\(project\) => \(/g, `projects.map((project: any) => {
    const p = {
      id: project.project_id,
      name: project.name,
      unit: project.unit,
      asset: project.asset,
      status: project.status,
      statusColor: project.status === 'Completed' ? 'text-[#22C55E]' : 'text-[#3B82F6]',
      statusBg: 'bg-[#3B82F6]/10 border-[#3B82F6]/25',
      risk: project.risk,
      riskColor: project.risk === 'HIGH' ? 'text-[#EF4444]' : 'text-[#F59E0B]',
      progress: project.progress,
      lastActivity: project.updated_at,
      files: 0,
      artifacts: 0,
      classification: project.classification,
    };
    return (
`);
content = content.replace(/project\.id/g, 'p.id');
content = content.replace(/project\.name/g, 'p.name');
content = content.replace(/project\.unit/g, 'p.unit');
content = content.replace(/project\.asset/g, 'p.asset');
content = content.replace(/project\.risk/g, 'p.risk');
content = content.replace(/project\.riskColor/g, 'p.riskColor');
content = content.replace(/project\.status/g, 'p.status');
content = content.replace(/project\.statusBg/g, 'p.statusBg');
content = content.replace(/project\.statusColor/g, 'p.statusColor');
content = content.replace(/project\.classification/g, 'p.classification');
content = content.replace(/project\.progress/g, 'p.progress');
content = content.replace(/project\.lastActivity/g, 'p.lastActivity');
content = content.replace(/project\.files/g, 'p.files');
content = content.replace(/project\.artifacts/g, 'p.artifacts');

content = content.replace(/<\/div>\n            <\/div>\n          \)\)/g, '</div>\n            </div>\n          );\n})');

fs.writeFileSync(file, content);
