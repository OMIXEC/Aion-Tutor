"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { OnboardingScreen } from "@/components/onboarding-screen";
import { supabase } from "@/lib/supabase";
import { useAppStore } from "@/lib/store";

export default function OnboardingPage() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(true);
    const [userId, setUserId] = useState<string | null>(null);

    useEffect(() => {
        const checkUser = async () => {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) {
                router.push("/");
                return;
            }
            setUserId(session.user.id);
            // Optionally check if they already have a profile
            const { data } = await supabase.from("profiles").select("*").eq("id", session.user.id).single();
            if (data) {
                useAppStore.getState().setProfile(data);
                router.push("/session");
            } else {
                setIsLoading(false);
            }
        };
        checkUser();
    }, [router]);

    const handleComplete = async (profileData: any) => {
        if (!userId) return;

        const newProfile = {
            id: userId,
            goal: profileData.goals,
            mission: profileData.primary_topics,
            knowledge: profileData.knowledge,
            certifications: profileData.certifications,
            experience_level: profileData.experience_level,
            use_deep_search: profileData.use_deep_search
        };

        const { error } = await supabase.from("profiles").upsert(newProfile);
        
        if (!error) {
            useAppStore.getState().setProfile(newProfile as any);
            router.push("/session");
        } else {
            console.error("Profile creation failed:", error);
            // Fallback for demo
            useAppStore.getState().setProfile(newProfile as any);
            router.push("/session");
        }
    };

    if (isLoading) {
        return <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-500">Personalizing your engine...</div>;
    }

    return <OnboardingScreen onComplete={handleComplete} />;
}
