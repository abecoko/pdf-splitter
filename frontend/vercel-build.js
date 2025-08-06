import { execSync } from 'child_process';

try {
  console.log('Installing dependencies...');
  execSync('npm ci', { stdio: 'inherit' });
  
  console.log('Building application...');
  execSync('npm run build', { stdio: 'inherit' });
  
  console.log('Build completed successfully!');
} catch (error) {
  console.error('Build failed:', error.message);
  process.exit(1);
}