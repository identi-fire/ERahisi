const path = require('path');

module.exports = {
  entry: './src/main.js', // Entry point for your JavaScript
  output: {
    filename: 'bundle.js', // Output JavaScript bundle name
    path: path.resolve(__dirname, 'dist'), // Output directory
  },
};