interface PhoneNumber {
  phone: string | null;
  name: string | null;
  description: string | null;
  type: string | null;
}

interface Location {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  description: string;
}

interface Service {
  id: number;
  ParentId: number | null;
  PublicName: string;
  Score: number | null;
  ServiceArea: string[] | null;
  Distance: string | null;
  Description: string | null;
  Latitude: number | null;
  Longitude: number | null;
  PhysicalAddressStreet1: string | null;
  PhysicalAddressStreet2: string | null;
  PhysicalAddressCity: string | null;
  PhysicalAddressProvince: string | null;
  PhysicalAddressPostalCode: string | null;
  PhysicalAddressCountry: string | null;
  MailingAttentionName: string | null;
  MailingAddressStreet1: string | null;
  MailingAddressStreet2: string | null;
  MailingAddressCity: string | null;
  MailingAddressProvince: string | null;
  MailingAddressPostalCode: string | null;
  MailingAddressCountry: string | null;
  PhoneNumbers: PhoneNumber[];
  Website: string | null;
  Email: string | null;
  Hours: string | null;
  Hours2: string | null;
  MinAge: string | null;
  MaxAge: string | null;
  UpdatedOn: string | null;
  TaxonomyTerm: string | null;
  TaxonomyTerms: string | null;
  TaxonomyCodes: string | null;
  Eligibility: string | null;
  FeeStructureSource: string | null;
  OfficialName: string | null;
  PhysicalCity: string | null;
  UniqueIDPriorSystem: string | null;
  RecordOwner: string | null;
}

export type { Service, PhoneNumber, Location };
