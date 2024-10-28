interface Address {
  street1: string | null;
  street2: string | null;
  city: string | null;
  province: string | null;
  postal_code: string | null;
  country: string | null;
  attention_name: string | null;
}

interface PhoneNumber {
  number: string;
  type: string | null;
  name: string | null;
  description: string | null;
  extension: string | null;
}

interface OperatingHours {
  day: string;
  is_open: boolean;
  is_24hour: boolean;
  open_time: string | null;
  close_time: string | null;
}

interface Service {
  id: number;
  name: string;
  service_type: string;
  source_id: string | null;
  official_name: string | null;

  // Location
  latitude: number;
  longitude: number;
  distance: number | null;
  physical_address: Address | null;
  mailing_address: Address | null;

  // Contact information
  phone_numbers: PhoneNumber[];
  fax: string | null;
  email: string | null;
  website: string | null;
  social_media: Record<string, string>;

  // Service details
  description: string | null;
  services: string[];
  languages: string[];
  taxonomy_terms: string[];
  taxonomy_codes: string[];

  // Operating information
  status: string | null;
  regular_hours: OperatingHours[];
  hours_exceptions: OperatingHours[];
  timezone_offset: string | null;

  // Accessibility and special features
  wheelchair_accessible: string;
  parking_type: string | null;
  accepts_new_patients: boolean | null;
  wait_time: number | null;

  // Booking capabilities
  has_online_booking: boolean;
  has_queue_system: boolean;
  accepts_walk_ins: boolean;
  can_book: boolean;

  // Eligibility and fees
  eligibility_criteria: string | null;
  fee_structure: string | null;
  min_age: number | null;
  max_age: number | null;

  // Metadata
  last_updated: Date | null;
  record_owner: string | null;
  data_source: string | null;
}

// Location interface for map functionality
interface Location {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  description: string;
}

export type { Service, PhoneNumber, Location, Address, OperatingHours };
