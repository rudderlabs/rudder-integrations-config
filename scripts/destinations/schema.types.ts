interface SchemaDefinition {
  name: string;
  description?: string;
  platform?: string;
  categories?: string[];
  website?: string;
  presets?: Array<{
    name: string;
    description?: string;
    subscribe?: string[];
  }>;
  authentication?: {
    scheme: string;
    fields: Record<
      string,
      {
        type: string;
        required?: boolean;
        description?: string;
        default?: any;
        sensitive?: boolean;
      }
    >;
  };
  settings?: {
    fields: Record<
      string,
      {
        type: string;
        required?: boolean;
        description?: string;
        default?: any;
        allowNull?: boolean;
        properties?: Record<
          string,
          {
            type: string;
            description?: string;
          }
        >;
        items?: {
          type: string;
          properties?: Record<
            string,
            {
              type: string;
              description?: string;
            }
          >;
        };
      }
    >;
  };
  actions?: Array<{
    name: string;
    description?: string;
    platform?: string;
    defaultSubscription: string;
    fields: Record<
      string,
      {
        type: string;
        required?: boolean;
        description?: string;
        default?: any;
        properties?: Record<
          string,
          {
            type: string;
            description?: string;
          }
        >;
      }
    >;
  }>;
  idResolution?: {
    type: string;
    scheme: string;
    fields: Record<
      string,
      {
        type: string;
        required?: boolean;
        description?: string;
      }
    >;
  };
}

// Helper type for field definitions
interface SchemaField {
  type: string;
  required?: boolean;
  description?: string;
  default?: any;
  sensitive?: boolean;
  allowNull?: boolean;
  properties?: Record<
    string,
    {
      type: string;
      description?: string;
    }
  >;
  items?: {
    type: string;
    properties?: Record<
      string,
      {
        type: string;
        description?: string;
      }
    >;
  };
}

export type { SchemaDefinition, SchemaField };
