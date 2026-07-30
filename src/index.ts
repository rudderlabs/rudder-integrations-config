import validator from './validator';

export {
  auditDestinationClientConfigMetadata,
  filterDestinationClientVisibleConfig,
  getDestinationClientVisibleConfigKeys,
} from './destinationConfig';

export const {
  validateConfig,
  validateSourceDefinitions,
  validateDestinationDefinitions,
  validateAccountDefinitions,
  init,
} = validator;
