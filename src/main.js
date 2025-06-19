import core from "@actions/core";
import github from "@actions/github";
import path from "path";
import fetch from "node-fetch";
import sharp from "sharp";

const IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg"];
const COLORBLIND_TYPES = ["protanopia", "deuteranopia", "tritanopia"];

async function run() {
    try {
        const token = core.getInput("repo-token", { required: false }) || process.env.GITHUB_TOKEN;
        if (!token) {
            throw new Error("GitHub token not provided. Set 'repo-token' input or GITHUB_TOKEN env variable.");
        }
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
