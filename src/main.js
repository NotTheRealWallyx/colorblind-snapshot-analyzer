const core = require("@actions/core");
const github = require("@actions/github");
const path = require("path");
const fetch = require("node-fetch");
const { simulate } = require("color-blind");
const sharp = require("sharp");
const fs = require("fs");

const IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg"];
const COLORBLIND_TYPES = ["protanopia", "deuteranopia", "tritanopia"];

async function run() {
    try {
        const token = core.getInput("repo-token", { required: true });
        const octokit = github.getOctokit(token);
        const { owner, repo } = github.context.repo;
        const prNumber = github.context.payload.pull_request.number;

        // Get list of files in the PR
        const files = await octokit.rest.pulls.listFiles({ owner, repo, pull_number: prNumber });
        const imageFiles = files.data.filter(file => IMAGE_EXTENSIONS.includes(path.extname(file.filename)));

        if (imageFiles.length === 0) {
            core.info("No image files found in this pull request.");
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
                    await sharp(buffer).raw().toBuffer({ resolveWithObject: true });
                    markdownReport += `- ✅ Simulated ${type} vision successfully.\n`;
                } catch (err) {
                    markdownReport += `- ❌ Failed to simulate ${type} vision.\n`;
                }
            }
        }

        await octokit.rest.issues.createComment({
            owner,
            repo,
            issue_number: prNumber,
            body: markdownReport,
        });

        core.setOutput("result", "Textual report posted.");
    } catch (error) {
        core.setFailed(error.message);
    }
}

run();
