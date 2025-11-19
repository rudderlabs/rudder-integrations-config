# AndroidKotlin and iOSSwift Migration Tracking

## Summary

**Total Destinations to Update:** 171
**Completed:** 0
**In Progress:** 0
**Remaining:** 171

## Excluded Destinations (Already Configured)

These destinations already have AndroidKotlin and/or iOSSwift support and are excluded from this migration:

- ✅ **adj** (Adjust) - Has both AndroidKotlin and iOSSwift
- ✅ **af** (AppsFlyer) - Has both AndroidKotlin and iOSSwift
- ✅ **braze** (Braze) - Has both AndroidKotlin and iOSSwift
- ✅ **fb** (Facebook App Events) - Has both AndroidKotlin and iOSSwift
- ✅ **firebase** (Firebase) - Device mode only, excluded from cloud mode migration
- ✅ **webhook** (Webhook) - Has both AndroidKotlin and iOSSwift

## Migration Requirements Per Destination

For each destination, the following changes are required:

1. **db-config.json** (MANDATORY)

   - Add `"androidKotlin"` and `"iosSwift"` to `supportedSourceTypes` array
   - Add cloud mode entries in `supportedConnectionModes` for both sources
   - Add message type mappings in `supportedMessageTypes.device` (if applicable)
   - Add configuration sections in `destConfig` (if applicable)

2. **schema.json** (MANDATORY)

   - Regenerate using V2 schema generator (preserves formatting, never removes fields):
   - Command: `python3 configure-cloud-mode-sources-for-mobile-sources/schemaGenerator/schemaGeneratorV2.py -name="<destination>" -update destination`

3. **ui-config.json** (CONDITIONAL)

   - Only if destination has source-specific prerequisite fields
   - Add corresponding androidKotlin and iosSwift field entries

4. **Tests** (CONDITIONAL)
   - Only update tests that reference Android/iOS sources
   - No new tests required

## Validation Checklist (Per Batch)

After completing each batch:

- [ ] All db-config.json files updated
- [ ] All ui-config.json files updated where applicable
- [ ] All schema.json files regenerated using V2 generator: `python3 configure-cloud-mode-sources-for-mobile-sources/schemaGenerator/schemaGeneratorV2.py -name="<destination>" -update destination`
- [ ] Tests updated and passing: `npm test`
- [ ] No linting errors: `npm run check:lint`
- [ ] Schema validation passes
- [ ] Tracking document updated with completion status
