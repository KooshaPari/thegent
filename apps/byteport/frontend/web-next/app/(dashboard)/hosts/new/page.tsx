'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardHeader } from '@/components/layout/Header';
import { HostSetupWizard } from '@/components/host-setup-wizard';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function RegisterHostPage() {
  const router = useRouter();
  const [isRegistering, setIsRegistering] = useState(false);

  const handleSuccess = (hostId: string) => {
    router.push(`/hosts/${hostId}`);
  };

  const handleCancel = () => {
    router.push('/hosts');
  };

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <DashboardHeader
        title="Register New Host"
        subtitle="Add a new host to your infrastructure"
        action={
          <Button variant="outline" onClick={handleCancel} disabled={isRegistering}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Cancel
          </Button>
        }
      />

      <section className="flex-1 overflow-y-auto px-6 py-8">
        <div className="max-w-4xl mx-auto">
          <HostSetupWizard
            onSuccess={handleSuccess}
            onCancel={handleCancel}
            onRegisteringChange={setIsRegistering}
          />
        </div>
      </section>
    </div>
  );
}
