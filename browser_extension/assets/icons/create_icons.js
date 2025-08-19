const fs = require('fs');
const { createCanvas } = require('canvas');

// Create icons programmatically
function createIcon(size) {
    const canvas = createCanvas(size, size);
    const ctx = canvas.getContext('2d');
    
    // Clear canvas
    ctx.clearRect(0, 0, size, size);
    
    // Background circle
    ctx.fillStyle = '#4F46E5';
    ctx.beginPath();
    ctx.arc(size/2, size/2, size/2 - 2, 0, 2 * Math.PI);
    ctx.fill();
    
    // Document icon (simple white rectangle)
    const docSize = size * 0.4;
    const docX = size * 0.25;
    const docY = size * 0.2;
    
    ctx.fillStyle = 'white';
    ctx.fillRect(docX, docY, docSize, docSize * 1.2);
    
    // Form lines (simple rectangles)
    ctx.fillStyle = '#4F46E5';
    const lineHeight = Math.max(1, size * 0.02);
    const lineSpacing = size * 0.08;
    const lineWidth = docSize * 0.7;
    const linesStartY = docY + size * 0.08;
    
    for (let i = 0; i < 4; i++) {
        ctx.fillRect(docX + size * 0.05, linesStartY + i * lineSpacing, lineWidth, lineHeight);
    }
    
    // AI dot (green circle)
    ctx.fillStyle = '#10B981';
    ctx.beginPath();
    ctx.arc(size * 0.75, size * 0.75, size * 0.12, 0, 2 * Math.PI);
    ctx.fill();
    
    // Small white dots for AI eyes (only for larger icons)
    if (size >= 48) {
        ctx.fillStyle = 'white';
        const eyeSize = size * 0.02;
        ctx.beginPath();
        ctx.arc(size * 0.72, size * 0.72, eyeSize, 0, 2 * Math.PI);
        ctx.fill();
        
        ctx.beginPath();
        ctx.arc(size * 0.78, size * 0.72, eyeSize, 0, 2 * Math.PI);
        ctx.fill();
    }
    
    return canvas;
}

// Create all required icon sizes
const sizes = [16, 48, 128];

sizes.forEach(size => {
    const canvas = createIcon(size);
    const buffer = canvas.toBuffer('image/png');
    const filename = `icon-${size}.png`;
    
    fs.writeFileSync(filename, buffer);
    console.log(`Created ${filename} (${size}x${size})`);
});

console.log('All icon files created successfully!');