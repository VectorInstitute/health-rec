interface PhoneNumber {
  number: string;
  type?: string | null;
  name?: string | null;
  description?: string | null;
  extension?: string | null;
}

interface Address {
  street1?: string | null;
  street2?: string | null;
  city?: string | null;
  province?: string | null;
  postal_code?: string | null;
  country?: string | null;
}

interface Service {
  // Required fields
  id: string;
  name: string;
  description: string;
  latitude: number;
  longitude: number;
  phone_numbers: PhoneNumber[];
  address: Address;
  email: string;

  // Optional fields
  metadata: Record<string, unknown>;
  last_updated?: string | null;
}

interface Location {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  description: string;
  address: string;
  rating?: number;
  reviewCount?: number;
  phone?: string;
}

interface Recommendation {
  message: string;
  is_emergency: boolean;
  is_out_of_scope: boolean;
  services?: Service[] | null;
  no_services_found: boolean;
}

interface Query {
  query: string;
  latitude?: number | null;
  longitude?: number | null;
  radius?: number | null;
}

export type { Service, PhoneNumber, Address, Location, Recommendation, Query };
