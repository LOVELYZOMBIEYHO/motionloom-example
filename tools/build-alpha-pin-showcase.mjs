#!/usr/bin/env node

import fs from 'node:fs/promises';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const toolDir = path.dirname(fileURLToPath(import.meta.url));
const sharp = require(path.join(toolDir, '../../anica-landing-page/node_modules/sharp'));

const [dslPath, renderedPngPath] = process.argv.slice(2);
if (!dslPath || !renderedPngPath) {
  throw new Error('Usage: build-alpha-pin-showcase.mjs DSL_FILE RENDERED_BIND_POSE_PNG');
}

const image = await sharp(renderedPngPath).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
const { width, height, channels } = image.info;
const pixels = image.data;
const pixelCount = width * height;
const corners = [0, width - 1, (height - 1) * width, pixelCount - 1];
const background = [0, 1, 2, 3].map((channel) => (
  corners.reduce((sum, index) => sum + pixels[index * channels + channel], 0) / corners.length
));
const backgroundDistance = (index) => {
  const offset = index * channels;
  const dr = pixels[offset] - background[0];
  const dg = pixels[offset + 1] - background[1];
  const db = pixels[offset + 2] - background[2];
  const da = pixels[offset + 3] - background[3];
  return Math.sqrt(dr * dr + dg * dg + db * db + da * da * 0.25);
};

// Flood-fill only edge-connected background. Enclosed white artwork such as
// eyes and shoes therefore remains part of the character surface.
const exterior = new Uint8Array(pixelCount);
const queue = new Int32Array(pixelCount);
let head = 0;
let tail = 0;
const enqueue = (index) => {
  if (exterior[index] || backgroundDistance(index) > 34) return;
  exterior[index] = 1;
  queue[tail++] = index;
};
for (let x = 0; x < width; x += 1) {
  enqueue(x);
  enqueue((height - 1) * width + x);
}
for (let y = 0; y < height; y += 1) {
  enqueue(y * width);
  enqueue(y * width + width - 1);
}
while (head < tail) {
  const index = queue[head++];
  const x = index % width;
  const y = Math.floor(index / width);
  if (x > 0) enqueue(index - 1);
  if (x + 1 < width) enqueue(index + 1);
  if (y > 0) enqueue(index - width);
  if (y + 1 < height) enqueue(index + width);
}

// A detailed landscape grid gives the relatively small full-body character
// enough vertices around fingers, neck, and ankles.
const cols = 96;
const rows = 54;
const cellCols = cols - 1;
const cellRows = rows - 1;
const occupied = new Uint8Array(cellCols * cellRows);
for (let y = 0; y < height; y += 1) {
  for (let x = 0; x < width; x += 1) {
    const index = y * width + x;
    if (exterior[index] || pixels[index * channels + 3] <= 8) continue;
    const col = Math.min(cellCols - 1, Math.floor(x * cellCols / width));
    const row = Math.min(cellRows - 1, Math.floor(y * cellRows / height));
    occupied[row * cellCols + col] = 1;
  }
}
const expanded = occupied.slice();
for (let row = 0; row < cellRows; row += 1) {
  for (let col = 0; col < cellCols; col += 1) {
    if (!occupied[row * cellCols + col]) continue;
    for (let dy = -1; dy <= 1; dy += 1) {
      for (let dx = -1; dx <= 1; dx += 1) {
        const nextCol = col + dx;
        const nextRow = row + dy;
        if (nextCol >= 0 && nextCol < cellCols && nextRow >= 0 && nextRow < cellRows) {
          expanded[nextRow * cellCols + nextCol] = 1;
        }
      }
    }
  }
}

const vertices = [];
const vertexIndex = new Map();
const triangles = [];
const ensureVertex = (gridIndex) => {
  if (vertexIndex.has(gridIndex)) return vertexIndex.get(gridIndex);
  const col = gridIndex % cols;
  const row = Math.floor(gridIndex / cols);
  const index = vertices.length;
  vertices.push({
    x: width * col / (cols - 1),
    y: height * row / (rows - 1),
  });
  vertexIndex.set(gridIndex, index);
  return index;
};
for (let row = 0; row < cellRows; row += 1) {
  for (let col = 0; col < cellCols; col += 1) {
    if (!expanded[row * cellCols + col]) continue;
    const topLeft = row * cols + col;
    const topRight = topLeft + 1;
    const bottomLeft = topLeft + cols;
    const bottomRight = bottomLeft + 1;
    triangles.push([
      ensureVertex(topLeft),
      ensureVertex(topRight),
      ensureVertex(bottomRight),
    ]);
    triangles.push([
      ensureVertex(topLeft),
      ensureVertex(bottomRight),
      ensureVertex(bottomLeft),
    ]);
  }
}

const number = (value) => Number(value.toFixed(2)).toString();
const indent = '              ';
const topology = [
  `${indent}<MeshTopology id="character_alpha_surface" mode="alpha">`,
  ...vertices.map((vertex, index) => (
    `${indent}  <Vertex id="character_surface_v${index}" x="${number(vertex.x)}" y="${number(vertex.y)}" />`
  )),
  ...triangles.map((triangle, index) => (
    `${indent}  <Triangle id="character_surface_t${index}" `
      + `a="character_surface_v${triangle[0]}" `
      + `b="character_surface_v${triangle[1]}" `
      + `c="character_surface_v${triangle[2]}" />`
  )),
  `${indent}</MeshTopology>`,
].join('\n');

const pins = [
  ['character_head_pin', 960, 165, 70],
  ['character_neck_pin', 960, 245, 48],
  ['character_chest_pin', 960, 340, 62],
  ['character_pelvis_pin', 960, 535, 64],
  ['character_left_shoulder_pin', 1028, 305, 52],
  ['character_right_shoulder_pin', 892, 305, 52],
  ['character_left_elbow_pin', 1086, 415, 48],
  ['character_right_elbow_pin', 834, 415, 48],
  ['character_left_hand_pin', 1145, 535, 46],
  ['character_right_hand_pin', 770, 535, 46],
  ['character_left_knee_pin', 1006, 745, 50],
  ['character_right_knee_pin', 914, 745, 50],
  ['character_left_foot_pin', 1018, 965, 46],
  ['character_right_foot_pin', 897, 965, 46],
].map(([id, x, y, radius]) => (
  `${indent}<PuppetPin id="${id}" role="position" `
    + `x="${x}" y="${y}" targetX="${x}" targetY="${y}" `
    + `radius="${radius}" strength="1" falloff="rigid" />`
)).join('\n');

const warp = `
            <!--
              Quick Puppet Surface Pins: one alpha-clipped character surface
              with more than three arbitrary controls. Rigid plateau influence
              keeps each body region stable while head, neck, torso, limb joints,
              both hands, and both feet remain directly draggable.
            -->
            <PuppetWarp id="character_full_surface_puppet"
                        target="@layer" capture="before"
                        mesh="alpha" solver="soft"
                        width="${width}" height="${height}" density="${cols}x${rows}">
${topology}
${pins}
            </PuppetWarp>`;

const source = await fs.readFile(dslPath, 'utf8');
const generatedWarp = /\n\s*<!--\s*Quick Puppet Surface Pins:[\s\S]*?<\/PuppetWarp>/;
const existingWarp = /\n\s*<!--\s*True Universal arm rig:[\s\S]*?<\/PuppetWarp>/;
const fallbackWarp = /\n\s*<PuppetWarp id="hair_touch_universal_arm"[\s\S]*?<\/PuppetWarp>/;
const matcher = generatedWarp.test(source)
  ? generatedWarp
  : existingWarp.test(source)
    ? existingWarp
    : fallbackWarp;
if (!matcher.test(source)) {
  throw new Error('Could not find the existing Showcase 64 PuppetWarp block.');
}
await fs.writeFile(dslPath, source.replace(matcher, warp));
console.log(`Wrote ${vertices.length} vertices, ${triangles.length} triangles, and 14 pins to ${dslPath}`);
