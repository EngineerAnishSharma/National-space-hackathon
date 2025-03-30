const fs = require('fs');
const path = require('path');

const sourceDir = path.join(__dirname, '../../generate-dataset');
const targetDir = path.join(__dirname, '../public/data');

// Ensure target directory exists
if (!fs.existsSync(targetDir)) {
  fs.mkdirSync(targetDir, { recursive: true });
}

['items.csv', 'containers.csv'].forEach(filename => {
  const content = fs.readFileSync(path.join(sourceDir, filename), 'utf8');
  const cleanContent = content
    .split('\n')
    .filter(line => line.trim() && !line.startsWith('//'))
    .join('\n');
  fs.writeFileSync(path.join(targetDir, filename), cleanContent);
});
