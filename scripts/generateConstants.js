const fs = require('fs');
const path = require('path');

// Path to the templates and generated files
const templatesDir = path.join(__dirname, '../templates');
const generatedDir = path.join(__dirname, '../generated');
const destinationsDir = path.join(__dirname, '../src/configurations/destinations');

const languageMap = {
    "web": ["ts"],
    "flutter": ["dart"],
    "ios": ["java", "m", "swift"],
    "android": ["kt", "java"]
};

// Function to check if the template should be generated for a specific language
function filterLanguages(destination, langCode) {
    const { supportedConnectionModes } = destination.config;
    // Filtering logic
    return Object.keys(supportedConnectionModes)
        .filter(platform => {
            const modes = supportedConnectionModes[platform];
            // Check if "device" or "hybrid" mode is present
            return (
                modes.includes("device") ||
                modes.includes("hybrid")
            )
        })
        .some(platform => languageMap[platform]?.includes(langCode));

}

// Check if the generated directory exists, if not, create it
if (!fs.existsSync(generatedDir)) {
    fs.mkdirSync(generatedDir, { recursive: true });
    console.log('Created "generated/" directory');
}

// Function to read the template file and process it
function processTemplate(template, data) {
    // Create a function to evaluate the template with the data
    // eslint-disable-next-line no-new-func
    return new Function('destinations', `return \`${template}\`;`)(data);
}

// Ensure the 'generated' directory exists
if (!fs.existsSync(generatedDir)) {
    fs.mkdirSync(generatedDir);
}

function prepareDestinations(langCode) {
    return fs.readdirSync(destinationsDir)
        .map((destination) => {
            const destinationsFilePath = path.join(destinationsDir, destination, "db-config.json");
            const destinationsContent = fs.readFileSync(destinationsFilePath, 'utf8');
            return JSON.parse(destinationsContent);
        })
        .filter((destination) => filterLanguages(destination, langCode))
        .map((destination) => ({ name: destination.name, displayName: destination.displayName }));
}

// Function to get the language code from the template file name
// Format: <template-name>.<lang-code>.template
function getLangCode(templateFileName) {
    return templateFileName.split('.')[1];
}

// Function to read and process templates in the templates folder
function generateFiles() {
    // Read all files in the templates directory
    fs.readdirSync(templatesDir)
        .filter((file) => file.endsWith('.template'))
        .forEach((file) => {
            const filePath = path.join(templatesDir, file);

            const destinations = prepareDestinations(getLangCode(file));

            // Read the content of the template file
            const templateContent = fs.readFileSync(filePath, 'utf8');

            // Process the template with the destinations data
            const output = processTemplate(templateContent, destinations);

            // Generate the output filename by removing the '.template' extension
            const outputFilePath = path.join(generatedDir, file.replace('.template', ''));

            // Write the generated content to the output file
            fs.writeFileSync(outputFilePath, output);
            console.log(`Generated: ${outputFilePath}`);

        });
}

// Generate the files
generateFiles();
