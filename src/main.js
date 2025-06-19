import core from '@actions/core';
import github from '@actions/github';
import path from 'path';
import fetch from 'node-fetch';
import sharp from 'sharp';
import pkg from 'color-blind';
const { simulate } = pkg;

const IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg'];
const COLORBLIND_TYPES = ['protanopia', 'deuteranopia', 'tritanopia'];

async function run() {
    try {
        const token =
            core.getInput('repo-token', { required: false }) ||
            process.env.GITHUB_TOKEN;
        if (!token) {
            throw new Error(
                "GitHub token not provided. Set 'repo-token' input or GITHUB_TOKEN env variable."
            );
        }
        const octokit = github.getOctokit(token);
        const { owner, repo } = github.context.repo;
        const prNumber = github.context.payload.pull_request.number;

        const files = await octokit.rest.pulls.listFiles({
            owner,
            repo,
            pull_number: prNumber,
        });
        const imageFiles = files.data.filter((file) =>
            IMAGE_EXTENSIONS.includes(path.extname(file.filename))
        );

        const pr = await octokit.rest.pulls.get({
            owner,
            repo,
            pull_number: prNumber,
        });
        const prBody = pr.data.body || '';
        const imageMarkdownRegex = /!\[[^\]]*\]\(([^)]+)\)/g;
        let match;
        const prImageUrls = [];
        while ((match = imageMarkdownRegex.exec(prBody)) !== null) {
            prImageUrls.push(match[1]);
        }

        if (imageFiles.length === 0 && prImageUrls.length === 0) {
            core.info('No image files or PR body images found in this pull request.');
            return;
        }

        let markdownReport = `### 🎨 Colorblind Snapshot Report\n\n`;

        for (const file of imageFiles) {
            const rawUrl = file.raw_url;
            const response = await fetch(rawUrl);
            const buffer = await response.buffer();

            const fileName = path.basename(file.filename);
            markdownReport += `\n**${fileName}**:\n`;

            for (const type of COLORBLIND_TYPES) {
                try {
                    // Convert image buffer to PNG base64
                    const pngBuffer = await sharp(buffer).png().toBuffer();
                    const base64 = pngBuffer.toString('base64');
                    // Simulate colorblind vision
                    const simulatedBase64 = simulate(base64, type);
                    // Try to decode the simulated image (should be a base64 PNG)
                    const simulatedBuffer = Buffer.from(simulatedBase64, 'base64');
                    await sharp(simulatedBuffer).metadata();
                    markdownReport += `- ✅ Simulated ${type} vision successfully.\n`;
                } catch (err) {
                    console.error(`Error simulating ${type} for ${fileName}:`, err);
                    markdownReport += `- ❌ Failed to simulate ${type} vision. Error: ${err.message}\n`;
                }
            }
        }

        for (const url of prImageUrls) {
            try {
                const response = await fetch(url);
                const buffer = await response.buffer();
                const fileName = url.split('/').pop();
                markdownReport += `\n**[PR Body] ${fileName}**:\n`;
                for (const type of COLORBLIND_TYPES) {
                    try {
                        const pngBuffer = await sharp(buffer).png().toBuffer();
                        const base64 = pngBuffer.toString('base64');
                        const simulatedBase64 = simulate(base64, type);
                        const simulatedBuffer = Buffer.from(simulatedBase64, 'base64');
                        await sharp(simulatedBuffer).metadata();
                        markdownReport += `- ✅ Simulated ${type} vision successfully.\n`;
                    } catch (err) {
                        console.error(`Error simulating ${type} for [PR Body] ${fileName}:`, err);
                        markdownReport += `- ❌ Failed to simulate ${type} vision. Error: ${err.message}\n`;
                    }
                }
            } catch (err) {
                markdownReport += `\n**[PR Body] ${url}**: ❌ Failed to fetch or process image.\n`;
            }
        }

        await octokit.rest.issues.createComment({
            owner,
            repo,
            issue_number: prNumber,
            body: markdownReport,
        });

        core.setOutput('result', 'Textual report posted.');
    } catch (error) {
        core.setFailed(error.message);
    }
}

run();
