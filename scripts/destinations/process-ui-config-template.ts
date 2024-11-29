/* eslint-disable no-lonely-if */
/* eslint-disable no-param-reassign */
import { BaseField, NewStyleUIConfig } from './types';
import { removeDefaultSubRegex } from './utils';

// Extend BaseField to include all possible nested fields
interface TemplateField extends BaseField {
  fields?: TemplateField[];
  customFields?: TemplateField[];
  rowFields?: TemplateField[];
  columns?: TemplateField[];
  from?: TemplateField;
  to?: TemplateField;
  regex?: string;
  dynamicConfigSupported?: boolean;
}

const processTemplateField = (
  field: TemplateField,
  dynamicFields: string[],
  _parentKey?: string,
): void => {
  // Get the relevant key for dynamic field check
  const fieldKey = field.configKey || field.value || '';
  const isFieldDynamic = dynamicFields.includes(fieldKey);

  // If field is dynamic, add dynamicConfigSupported flag
  if (isFieldDynamic) {
    field.dynamicConfigSupported = true;
  } else {
    // Process regex if not a dynamic field
    if (field.regex) {
      field.regex = removeDefaultSubRegex(field.regex);
    }
  }

  // Process from/to fields for mapping components
  if (field.from) {
    processTemplateField(field.from, dynamicFields, fieldKey);
  }
  if (field.to) {
    processTemplateField(field.to, dynamicFields, fieldKey);
  }

  // Process nested fields
  if (field.fields) {
    field.fields.forEach((nestedField) => {
      processTemplateField(nestedField, dynamicFields, fieldKey);
    });
  }

  // Process custom fields
  if (field.customFields) {
    field.customFields.forEach((customField) => {
      processTemplateField(customField, dynamicFields, fieldKey);
    });
  }

  // Process row fields
  if (field.rowFields) {
    field.rowFields.forEach((rowField) => {
      processTemplateField(rowField, dynamicFields, fieldKey);
    });
  }

  // Process columns
  if (field.columns) {
    field.columns.forEach((column) => {
      processTemplateField(column, dynamicFields, fieldKey);
    });
  }
};

const processUIConfigTemplate = (template: NewStyleUIConfig, dynamicFields: string[]): void => {
  // Process base template
  if (template.baseTemplate) {
    template.baseTemplate.forEach((base: { sections: any[] }) => {
      base.sections?.forEach((section: { groups: any[] }) => {
        section.groups?.forEach((group: { fields: any[] }) => {
          group.fields?.forEach((field: TemplateField) => {
            processTemplateField(field as TemplateField, dynamicFields);
          });
        });
      });
    });
  }

  // Process SDK template
  if (template.sdkTemplate?.sections) {
    template.sdkTemplate.sections.forEach((section: any) => {
      section.groups?.forEach((group: { fields: any[] }) => {
        group.fields?.forEach((field: TemplateField) => {
          processTemplateField(field as TemplateField, dynamicFields);
        });
      });
    });
  }

  // Process consent settings template
  if (template.consentSettingsTemplate?.sections) {
    template.consentSettingsTemplate.sections.forEach((section: any) => {
      section.groups?.forEach((group: { fields: any[] }) => {
        group.fields?.forEach((field: TemplateField) => {
          processTemplateField(field as TemplateField, dynamicFields);
        });
      });
    });
  }

  // Process redirect groups
  if (template.redirectGroups) {
    Object.values(template.redirectGroups).forEach((group: unknown) => {
      const typedGroup = group as { tabs?: { fields?: TemplateField[] }[] };
      typedGroup.tabs?.forEach((tab) => {
        tab.fields?.forEach((field: TemplateField) => {
          processTemplateField(field as TemplateField, dynamicFields);
        });
      });
    });
  }
};

export { processUIConfigTemplate };
