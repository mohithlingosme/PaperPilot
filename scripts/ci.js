#!/usr/bin/env node
/**
 * Lightweight CI task router.
 * Each command exits 0 if the stack/config is missing so pipelines stay green until code is added.
 */
const fs = require("fs");
const { spawnSync } = require("child_process");

const task = process.argv[2] || "help";

const hasFile = (paths) => paths.some((p) => fs.existsSync(p));

const run = (cmd, args = []) => {
  const result = spawnSync(cmd, args, { stdio: "inherit", shell: true });
  if (result.status !== 0) {
    process.exit(result.status);
  }
};

const tasks = {
  lint: () => {
    if (fs.existsSync("node_modules/.bin/eslint")) {
      run("npm", ["run", "lint:frontend", "--if-present"]);
      run("npm", ["run", "lint:backend", "--if-present"]);
    } else {
      console.log("No lint config/tools found. Skipping.");
    }
  },
  typecheck: () => {
    if (fs.existsSync("tsconfig.json") || fs.existsSync("packages/tsconfig.json")) {
      run("npm", ["run", "typecheck:frontend", "--if-present"]);
      run("npm", ["run", "typecheck:backend", "--if-present"]);
    } else {
      console.log("No TypeScript config found. Skipping.");
    }
  },
  test: () => tasks["test:unit"](),
  "test:unit": () => {
    if (hasFile(["vitest.config.ts", "jest.config.ts", "jest.config.js"])) {
      run("npm", ["run", "test:unit:frontend", "--if-present"]);
      run("npm", ["run", "test:unit:backend", "--if-present"]);
    } else {
      console.log("No unit test config found. Skipping.");
    }
  },
  "test:e2e": () => {
    if (hasFile(["playwright.config.ts", "playwright.config.js", "cypress.config.ts", "cypress.config.js", "cypress.json"])) {
      run("npm", ["run", "test:e2e:playwright", "--if-present"]);
      run("npm", ["run", "test:e2e:cypress", "--if-present"]);
    } else {
      console.log("No E2E config found. Skipping.");
    }
  },
  build: () => {
    if (fs.existsSync("package.json")) {
      run("npm", ["run", "build:frontend", "--if-present"]);
      run("npm", ["run", "build:backend", "--if-present"]);
    } else {
      console.log("No build scripts found. Skipping.");
    }
  },
  prepare: () => {
    console.log("Nothing to prepare yet. Add dependency installation steps here when code is added.");
  },
  help: () => {
    console.log("Usage: node scripts/ci.js <lint|typecheck|test|test:unit|test:e2e|build>");
  },
};

(tasks[task] || tasks.help)();
